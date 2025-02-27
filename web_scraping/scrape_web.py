import requests
from bs4 import BeautifulSoup as bs
import os
from pprint import pprint


script_path = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(os.path.split(script_path)[0], 'data') #../data

def get_all_tables(soup):
    """Extracts and returns all tables in a soup object"""
    return soup.find_all("table")

def get_table_headers(table):
    """Given a table soup, returns all the headers"""
    headers = []
    for th in table.find("tr").find_all("th"):
        headers.append(th.text.strip())
    return headers

def get_table_rows(table):
    """Given a table, returns all its rows"""
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

    
    
def process_url(url):
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

def main():
    try:
        os.makedirs(data_dir)
    except:
        pass
    
    tables_list = process_url('https://catalog.unomaha.edu/undergraduate/college-information-science-technology/computer-science/computer-science-bs/#fouryearplantext')
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
            print(row)
            print(len(row))
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
                semester = row[0].upper()
            else:
                if row[0] != '' and len(row) == 3:
                    row.extend(row[0].split(u'\xa0'))
                    classes_in_semeseter.append(row)
        structured_rows[year] = {
            'semseter': semester,
            'classes': classes_in_semeseter
        }
        
        pprint(structured_rows)
                
    print("Finished")

if __name__ == '__main__':
    main()