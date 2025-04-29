## @package get_four_year
#  This module contains all of the functionality that is needed to process the four year plan that is given with some url. 
#
#  For proof of concept running this package as a script utilizes the Computer Science four year plan.

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

## From a url that contains a four year plan process it and produce a JSON file in a structure that we can utilize to then convert into a clingo file.
#
# For the page in the computer science four year plan, create a JSON file with the class content organized by year and semester. 
# This data is then used to discover conflicts that are higher priority.
#
#
# @params url A string containing the url for the page with the four year plan
# @params output_file 
# \parblock
# A string that contains the file path and filename that the JSON will be written to. 
# 
# *NOTE* to maintain the script's OS agnostic nature, 
# it is suggested to utilize os.path.join() to join strings or os.sep.join() to join elements of a list
# \endparblock
def read_four_year(url, output_file):
    
    tables_list = process_url(url)
    json_data = []
    for table in tables_list[1:]:
        structured_rows = {
            'First Year': {
                'FALL': [],
                'SPRING': []
            },
            'Second Year': {
                'FALL': [],
                'SPRING': []
            },
            'Third Year': {
                'FALL': [],
                'SPRING': []
            },
            'Fourth Year': {
                'FALL': [],
                'SPRING': []
            }
        }
        classes_in_semeseter = []
        year = ''
        semester = ''
        for row in table:
            # print(row)
            # print(len(row))
            if row[0] in structured_rows.keys():
                if semester != '':
                    structured_rows[year][semester] = classes_in_semeseter
                    classes_in_semeseter = []
                    semester = ''
                year = row[0]
                    
            elif row[0].upper() in structured_rows[year].keys():
                if semester != '':
                    structured_rows[year][semester] = classes_in_semeseter
                    classes_in_semeseter = []
                semester = row[0].upper()
            else:
                if row[0] != '' and len(row) == 3:
                    row[0] = row[0].replace(u'\xa0', ' ')
                    row[0] = row[0].split('or ')
                    row[1] = row[1].split('or ')
                    renamed_courses = []
                    for course in row[0]:
                        renamed_courses.append(course.upper().replace(' ', ''))
                        
                    row[0] = renamed_courses
                    classes_in_semeseter.append(row)
        structured_rows[year][semester] = classes_in_semeseter
        # pprint(structured_rows)
        json_data.append(structured_rows)
    print("Finished Gathering Data")
    
    with open(output_file, 'w') as f:
        json.dump(json_data,f, indent=4)
    
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
    filename = os.path.join(data_dir,'fourYearPlan.json')
    url = 'https://catalog.unomaha.edu/undergraduate/college-information-science-technology/computer-science/computer-science-bs/#fouryearplantext'
    read_four_year(url, filename)
