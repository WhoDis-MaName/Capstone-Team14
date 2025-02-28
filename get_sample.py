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
            sample_data[semester][department] = {class_name: classes[semester][department][class_name] for class_name in class_subset}
        

try:
    os.mkdir('samples')
except:
    pass

classes = get_classes('filtered.json')

for i in range(0,10):
    sample_data = create_sample(classes, 3, 2, 10)
    with open(os.path.join('samples',f'sample_{i}.json'), 'w') as f:
        json.dump(sample_data,f, indent=4)