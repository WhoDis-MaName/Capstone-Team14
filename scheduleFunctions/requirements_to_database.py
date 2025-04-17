import os
import json

from models import *

def store_requirements(json_file):
    with open(json_file, "r") as file:
        data = json.load(file)

    # If the JSON root is a list, assume it contains a dictionary
    if isinstance(data, list) and len(data) > 0:
        data = data[0]  # Take the first element

    if not isinstance(data, dict):
        raise ValueError(
            "Invalid JSON structure: Expected a dictionary at the top level."
        )
        
    for major_label in data.keys():
        for requirement_label in data[major_label].keys():
            requirement_query = Requirement.objects.filter(major_label=major_label, requirement_label=requirement_label)
            
            if not requirement_query.exists():
                courses = data[major_label][requirement_label]['classes']
                course_list = []
                for course in courses:
                    subject = course[:-4]
                    course_number = course[-4:]
                    selected_course = Course.objects.filter(subject = subject, class_number=course_number)
                    if selected_course.exists():
                        course_list.append(selected_course)
                    else:
                        new_course = Course(
                            subject = subject, 
                            class_number=course_number
                        )
                        new_course.save()
                        course_list.append(new_course)
                    
                 
                
                requirement = Requirement(
                    major_label = major_label,
                    requirement_label = requirement_label,
                    credits = data[major_label][requirement_label]['credits'],
                    course_options = course_list
                )
                requirement.save()
            

if __name__ == "__main__":
    if os.name == 'nt':
        current_directory = os.path.dirname(os.path.realpath(__file__)) # Get current directory
    else:
        current_directory = os.path.dirname(os.path.realpath(__name__)) # Get current directory
        

    path = current_directory.split(os.sep)

    root_index = path.index('Capstone-Team14')
    root_dir = os.sep.join(path[:root_index+1])
    data_dir = os.path.join(root_dir, 'data_files', 'requirements')
    filename = os.path.join(data_dir, 'requirements.json')