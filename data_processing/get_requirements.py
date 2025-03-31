import os
import json
from pprint import pprint

import requests
from bs4 import BeautifulSoup as bs



if os.name == 'nt':
    current_directory = os.path.dirname(os.path.realpath(__file__)) # Get current directory
else:
    current_directory = os.path.dirname(os.path.realpath(__name__)) # Get current directory
    

path = current_directory.split(os.sep)

root_index = path.index('Capstone-Team14')
root_dir = os.sep.join(path[:root_index+1])
data_dir = os.path.join(root_dir, 'data_files', 'four_year_plan')

def get_all_tables(soup: bs):
    """Finds all of the tables in the page gathered with BS4

    Args:
        soup (bs): The soup representation of the web page

    Returns:
        ResultSet: A set containing all of the instances of `<table></table>` along with all of its contents
    """
    return soup.find_all("table")

def get_table_rows(table) -> list:
    """Given a table, returns all its rows

    Args:
        table : table from web page grabbed using BS4 soup object

    Returns:
        list: a 2d list that represents all of the rows
    """
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

    
    
def process_url(url: str):
    """Take a url and find all of the tables contained in the page and return a ResultSet

    Args:
        url (str): URL of the page to be searched.

    Returns:
        ResultSet: Set containing all of the tables in the page
    """
    
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

def read_requirements(url):
    """
        Take url for a degree requirements list
    """

    
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
            ...
        
        # print('Adding result to list')
        json_data.append(structured_rows)
    return json_data

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
                ...
        ...
    return compiled_req

    
if __name__ == "__main__":
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
    requirements = []
    for url in urls:
        requirements.extend(read_requirements(url))
    # pprint(requirements)
    new_reqirements:dict = compile_requirements(requirements)
    # pprint(new_reqirements)
    with open(json_file, 'w') as f:
        json.dump(new_reqirements,f, indent=4)
        
