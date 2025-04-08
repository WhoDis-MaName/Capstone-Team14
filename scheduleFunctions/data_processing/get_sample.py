import os
import json
from random import sample

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
            class_list = {class_name: classes[semester][department][class_name] for class_name in class_subset}
            print(class_list)
            sample_data[semester][department] = class_list
            
    return sample_data

import os

if os.name == 'nt':
    current_directory = os.path.dirname(os.path.realpath(__file__)) # Get current directory
else:
    current_directory = os.path.dirname(os.path.realpath(__name__)) # Get current directory
    

path = current_directory.split(os.sep)

root_index = path.index('scheduleFunctions')
root_dir = os.sep.join(path[:root_index+1])
read_dir = os.path.join(root_dir, 'data_files', 'uploaded_schedule')
sample_dir = os.path.join(root_dir, 'data_files', 'samples')
try:
    os.makedirs(read_dir)
except:
    pass

try:
    os.makedirs(sample_dir)
except:
    pass

classes = get_classes(os.path.join(read_dir,'filtered.json'))

for i in range(0,10):
    sample_data = create_sample(classes, 1, 2, 5)
    print(sample_data)

    with open(os.path.join(sample_dir,f'sample_0{i}.json'), 'w') as f:
        json.dump(sample_data,f, indent=4)