## @package get_requirements
#  This module contains all of the functionality that is needed to process the degree requirements. 
#
#  For proof of concept, running this package as a script utilizes the degree requirments from all five Computer Science Concentrations.
import os
import json
from pprint import pprint

import requests
from bs4 import BeautifulSoup as bs

## Finds all of the tables in the page gathered with BS4
#
#  @param[in] soup The BeautifulSoup4 representation of the web page
#  @return A set containing all of the instances of `<table></table>` along with all of its contents

def get_all_tables(soup: bs):
    return soup.find_all("table")

## Given a table, returns all its rows
#
# @param[in] table A table from web page grabbed using BS4 soup object
# @return A 2d list that represents all of the rows from the table
def get_table_rows(table) -> list:
    rows = []
    for tr in table.find_all("tr")[0:]:
        cells = []
        # grab all td tags in this table row
        tds = tr.find_all("td")
        if len(tds) == 0:
            # if no td tags, search for th tags
            # can be found especially in wikipedia tables below the table
            ths = tr.find_all("th")
            for th in ths:
                cells.append(th.text.strip())
        else:
            # use regular td tags
            for td in tds:
                cells.append(td.text.strip())
        rows.append(cells)
    return rows

    
##  Take a url and find all of the tables contained in the page and return a ResultSet
# 
# @param url URL of the page to be searched.
# @return List containing all of the tables in the page. Each of table is a 2d array (list)

def process_url(url: str):
    
    tables_list = []
    # print(nfl_url)
    data = requests.get(url)
    if data.status_code != 200:
        print(data.status_code)
        print('Request failed at:',url)
        return tables_list
    response = bs(data.content, "html.parser")
    
    # extract all the tables from the web page
    tables_list = get_all_tables(response)
    print(f"[+] Found a total of {len(tables_list)} tables.")
    if len(tables_list) == 0:
        print(f'No Data: {url}')
    
    tables=[]
    for table in tables_list:
        tables.append(get_table_rows(table))
    return tables
    pass


## Read the requirements from a given url that contains degree requirements and process it into a dictionary
#
# @param url A string that contains the url that is to be read to find the degree requirements
# @return a dictionary that is structured to associate courses with the major and sub groups of requirements that are fulfilled
def read_requirements(url: str):
    
    tables_list = process_url(url)
    json_data = []
    for table in tables_list:
        structured_rows = {}
        classes_in_group = []
        major_group = ''
        group_name = ''
        group_credits = 0
        for row in table[1:]:
            if len(row) == 2:
                if row[0].startswith('or'):
                    row.append('')
                    print('Added column to row. New row length: ', len(row))
                elif not row[1].isdigit():
                    group_desc = row[0].split('-')
                    if group_desc[0] != 'ELECTIVES' and (len(group_desc) != 2 or group_desc[1].endswith('hrs')) :
                        
                        print(row)
                    elif group_desc[0] == 'ELECTIVES' or group_desc[1].strip()[0].isdigit() :                            
                        if group_name != '':
                            structured_rows[major_group][group_name] = {
                                'credits': group_credits,
                                'classes': classes_in_group
                            }
                        
                        major_group = group_desc[0].strip().replace(' ', '_').lower()
                        structured_rows[major_group] = {}
                        group_name = ''
                        group_credits = 0
                        
                else:
                    if major_group != '' and major_group not in structured_rows.keys():
                            structured_rows[major_group] = {}
                    if group_name != '':
                        structured_rows[major_group][group_name] = {
                            'credits': group_credits,
                            'classes': classes_in_group
                        }
                        classes_in_group = []
                    
                    group_name = row[0].split('-')[0].strip().replace(' ', '_').lower()
                    if group_name == 'all_of_the_following:':
                        group_name = '_'.join([major_group,'core'])
                    elif 'from_the_following' in group_name:
                        group_name = 'core_extension'
                    group_credits = int(row[1])
                    print('Storing group_name and group_credits:', group_name, group_credits)
                
            if len(row) == 3:
                # print('Adding row to group')
                classes_in_group.append(row[0].replace(u'\xa0', '').replace(u'or', '').lower())
            
            if len(row) != 2 and len(row) != 3:
                print(row)
            
        
        # print('Adding result to list')
        json_data.append(structured_rows)
    return json_data

## Gather multiple requirements sets and complile them so that the group names are unique
# 
# @param requirements A list containing dictionaries that are structured with classes in groups and sub-groups
# @return A single dictionary that combines all of the requirements into one while handling duplicate group labels by combining the class lists.
def compile_requirements(requirements: list[dict]) -> dict:
    compiled_req:dict = {}
    
    for req_dict in requirements:
        for major_group in req_dict.keys():
            if major_group not in compiled_req.keys():
                compiled_req[major_group] = {}
            for sub_group in req_dict[major_group].keys():
                temp_major = major_group
                if sub_group in ['math_courses', 'science_courses']:
                    if major_group not in ['major_requirements',]:
                        temp_major = 'major_requirements'
                
                if sub_group not in compiled_req[temp_major].keys():
                    compiled_req[temp_major][sub_group] = req_dict[major_group][sub_group]
                    continue
                
                compiled_req[temp_major][sub_group]['classes'] = list(set(compiled_req[temp_major][sub_group]['classes']).union(req_dict[major_group][sub_group]['classes']))
                if compiled_req[temp_major][sub_group]['credits'] != req_dict[major_group][sub_group]['credits']:
                    print(f'Credit count not the same for {major_group} - {sub_group}. Expecting {compiled_req[temp_major][sub_group]["credits"]}, got {req_dict[major_group][sub_group]["credits"]}')
                    max_credits = max(req_dict[major_group][sub_group]['credits'],compiled_req[temp_major][sub_group]['credits'])
                    print(f'Selecting {max_credits}')
                    compiled_req[temp_major][sub_group]['credits'] = max_credits
                
        
    return compiled_req

## Handle the processing of multiple degree requirements and sending it to a json file
#
# @param urls A list of url strings. Each url must direct to a page that contains requirements for some sort of degree
# @param json_file 
# \parblock
# A string that contains the file path and filename that the JSON will be written to. 
# 
# *NOTE* to maintain the script's OS agnostic nature, 
# it is suggested to utilize os.path.join() to join strings or os.sep.join() to join elements of a list
# \endparblock
def process_degree_requirements(urls: list[str], json_file: str) -> None:
    requirements = []
    for url in urls:
        requirements.extend(read_requirements(url))
    # pprint(requirements)
    new_reqirements:dict = compile_requirements(requirements)
    # pprint(new_reqirements)
    with open(json_file, 'w') as f:
        json.dump(new_reqirements,f, indent=4)

    
if __name__ == "__main__":
    if os.name == 'nt':
        current_directory = os.path.dirname(os.path.realpath(__file__)) # Get current directory
    else:
        current_directory = os.path.dirname(os.path.realpath(__name__)) # Get current directory
        

    path = current_directory.split(os.sep)

    root_index = path.index('Capstone-Team14')
    root_dir = os.sep.join(path[:root_index+1])
    data_dir = os.path.join(root_dir, 'data_files', 'four_year_plan')
    try:
        os.makedirs(data_dir)
    except:
        pass
    json_file = os.path.join(data_dir,'requirements.json')
    urls = [
        'https://catalog.unomaha.edu/undergraduate/college-information-science-technology/computer-science/computer-science-bs/artificialintelligence-concentraton/',
        'https://catalog.unomaha.edu/undergraduate/college-information-science-technology/computer-science/computer-science-bs/game-programming-concentration/',
        'https://catalog.unomaha.edu/undergraduate/college-information-science-technology/computer-science/computer-science-bs/internet-technologies-it-concentration-computer-science-majors/',
        'https://catalog.unomaha.edu/undergraduate/college-information-science-technology/computer-science/computer-science-bs/information-assurance-concentration/',
        'https://catalog.unomaha.edu/undergraduate/college-information-science-technology/computer-science/computer-science-bs/software-engineering-concentration/'
    ]
    process_degree_requirements(urls, json_file)
    
        
