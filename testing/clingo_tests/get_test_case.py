import os
import json
from random import sample

if os.name == 'nt':
    current_directory = os.path.dirname(os.path.realpath(__file__)) # Get current directory
else:
    current_directory = os.path.dirname(os.path.realpath(__name__)) # Get current directory

print(current_directory)

test_folder_dir = os.path.split(current_directory)[0]

def get_classes(filename: str) -> dict:
    classes = {}

    with open(filename, 'r') as f:
        classes = json.load(f)
        
    return classes

def create_sample(classes:dict, num_semesters:int, num_departments:int, num_classes:int) -> dict:
    sample_data = {}
    key_list = list(classes.keys())
    semester_subset = sample(key_list,min(num_semesters,len(key_list)))
    for semester in semester_subset:
        sample_data[semester] = {}
        key_list = list(classes[semester].keys())
        department_subset = sample(key_list,min(num_departments,len(key_list)))
        for department in department_subset:
            key_list = list(classes[semester][department].keys())
            class_subset = sample(key_list,min(num_classes,len(key_list)))
            for sample_class in class_subset:

                classes[semester][department][sample_class]['sections'] = {
                    list(classes[semester][department][sample_class]['sections'].keys())[0]: list(classes[semester][department][sample_class]['sections'].values())[0]
                    }
            class_list = {class_name: classes[semester][department][class_name] for class_name in class_subset}
            sample_data[semester][department] = class_list
            
    return sample_data

test_cases_dir = os.path.join(test_folder_dir,'test_cases')
try:
    os.mkdir(test_cases_dir)
except:
    pass

classes = get_classes('filtered.json')

for i in range(1,2):
    sample_data = create_sample(classes, 1, 2, 5)

    with open(os.path.join(test_cases_dir,f'test_case_0{i}.json'), 'w') as f:
        json.dump(sample_data,f, indent=4)