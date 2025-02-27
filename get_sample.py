import json
from random import sample

classes = {}

with open('filtered.json', 'r') as f:
    classes = json.load(f)
    
sample_data = {}
key_list = list(classes.keys())
semester_subset = sample(key_list,min(3,len(key_list)))
for semester in semester_subset:
    sample_data[semester] = {}
    for department in classes[semester].keys():
        key_list = list(classes[semester][department].keys())
        class_subset = sample(key_list,min(10,len(key_list)))
        sample_data[semester][department] = {class_name: classes[semester][department][class_name] for class_name in class_subset}
        

with open('sample.json', 'w') as f:
    json.dump(sample_data,f, indent=4)