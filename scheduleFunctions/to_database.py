import os
import json
import re
from datetime import datetime as date

from .models import *

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
                
def store_plan(json_file):
    ...
                
def store_schedule(json_file: str) -> None:
    with open(json_file, "r") as file:
        data = json.load(file)

    # If the JSON root is a list, assume it contains a dictionary
    if isinstance(data, list) and len(data) > 0:
        data = data[0]  # Take the first element

    if not isinstance(data, dict):
        raise ValueError(
            "Invalid JSON structure: Expected a dictionary at the top level."
        )
        
    schedule = data[max(data.keys())]
    for subject, courses in schedule:
        for course, details in courses:
            selected_course = Course.objects.filter(subject=subject, class_number=course)
            if not selected_course.exists():
                selected_course = Course(
                    subject = subject, 
                    class_number=course
                )
                
            selected_course.name = details["title"]
            selected_course.credits = details['sections'][details['sections'].keys()[0]]["Credit Hours"]
            selected_course.save()
            
            for section, section_details in details['sections']:
                if section_details['Location'] in ['Totally Online', 'To Be Announced']:
                    continue
                selected_section = Section.objects.filter(course=selected_course, section_number=int(section))
                if not selected_section.exists():
                    selected_section = Section(
                        course=selected_course, 
                        section_number=int(section)
                    ) 
                selected_section.section_id = int(section_details['Class Number'].split(" ")[0])
                selected_section.professor = section_details['Instructor']
                room_dict = re.search('(?P<building>.+)\s?(?P<room_number>[0-9]*)', section_details['Location'])
                selected_room = Room.objects.filter(building = room_dict.group('building'), room_number = int(room_dict.group('room_number')))
                if not selected_section.exists():
                    selected_room = Room(
                        building = room_dict.group('building'), 
                        room_number = int(room_dict.group('room_number')),
                        capacity = section_details['class_max']
                    )
                
                selected_room.capacity = max(selected_room.capacity, section_details['class_max'])
                selected_room.save()
                selected_section.room = selected_room
                
                start_time, end_time = section_details['Time'].split(' - ')
                
                start_time = date.strptime(start_time, "%-I:%M%p")
                end_time = date.strptime(end_time, "%-I:%M%p")
                
                selected_section.start_time = start_time
                selected_section.end_time = end_time
                
                days_list = Day.objects.filter(day_of_week__in=[Day.DAY_OF_WEEK_CHOICES[day] for day in section_details['Days']])
                selected_section.days = days_list
                selected_section.save()
