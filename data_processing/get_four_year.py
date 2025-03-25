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
    return tables_list
    pass

def read_four_year(url, output_file):
    """
        For the page in the computer science four year plan, create a JSON file with the class content organized by year and semester. 
        This data is then used to discover conflicts that are higher priority.
    """

    
    tables_list = process_url(url)
    json_data = []
    for table in tables_list[1:]:
        rows = get_table_rows(table)
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
        for row in rows:
            # print(row)
            # print(len(row))
            if row[0] in structured_rows.keys():
                if semester != '':
                    structured_rows[year][semester] = classes_in_semeseter
                    year = row[0]
                    classes_in_semeseter = []
                    semester = ''
                elif year == '':
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
                        renamed_courses.append(course.lower().replace(' ', ''))
                        
                    row[0] = renamed_courses
                    classes_in_semeseter.append(row)
        structured_rows[year][semester] = classes_in_semeseter
        # pprint(structured_rows)
        json_data.append(structured_rows)
    print("Finished Gathering Data")
    
    with open(output_file, 'w') as f:
        json.dump(json_data,f, indent=4)
    
if __name__ == "__main__":
    try:
        os.makedirs(data_dir)
    except:
        pass
    filename = os.path.join(data_dir,'fourYearPlan.json')
    url = 'https://catalog.unomaha.edu/undergraduate/college-information-science-technology/computer-science/computer-science-bs/#fouryearplantext'
    read_four_year(url, filename)
