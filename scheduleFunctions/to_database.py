import os
import json
import re
from pprint import pprint
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
                    course_number = int(course[-4:])
                    selected_course = Course.objects.filter(subject = subject, class_number=course_number)
                    if  not selected_course.exists():
                        selected_course = Course(
                            subject = subject, 
                            class_number=course_number,
                            weight = course_number // 1000
                        )
                        selected_course.save()
                        course_list.append(selected_course)
                    else:
                        course_list.extend(list(selected_course))
                    
                    
                 
                
                requirement = Requirement(
                    major_label = major_label,
                    requirement_label = requirement_label,
                    credits = data[major_label][requirement_label]['credits']
                )
                requirement.course_options.add(*course_list)
                requirement.save()
                
def store_plan(json_file) -> None:
    with open(json_file, "r") as file:
        data = json.load(file)

    # If the JSON root is a list, assume it contains a dictionary
    if isinstance(data, list) and len(data) > 0:
        data = data[0]  # Take the first element

    if not isinstance(data, dict):
        raise ValueError(
            "Invalid JSON structure: Expected a dictionary at the top level."
        )
    
    for course, course_details in data.items():
        subject = course[:-4]
        course_number = int(course[-4:])
        selected_course = Course.objects.filter(subject=subject, class_number=course_number)
        if not selected_course.exists():
            selected_course = Course(
                subject = subject, 
                class_number=course_number,
                weight = course_number // 1000
            )
        else:
            selected_course = list(selected_course)[0]
        selected_course.credits = int(course_details['credits'])
        
        equivalent_courses = []
        for other_course in course_details['equivalent_courses']:
            selected_other_course = Course.objects.filter(
                subject=other_course[:-4], 
                class_number=int(other_course[-4:]))
            if not selected_other_course.exists():
                selected_other_course = Course(
                    subject=other_course[:-4], 
                    class_number=int(other_course[-4:]),
                    weight = int(other_course[-4:]) // 1000
                )
                selected_other_course.save()
                same_semester.append(selected_other_course)
            else:
                same_semester.extend(list(selected_other_course))
        
        same_semester = []
        for other_course in course_details['same_semester']:
            selected_other_course = Course.objects.filter(
                subject=other_course[:-4], 
                class_number=int(other_course[-4:]))
            if not selected_other_course.exists():
                selected_other_course = Course(
                    subject=other_course[:-4], 
                    class_number=int(other_course[-4:]),
                    weight = int(other_course[-4:]) // 1000
                )
                selected_other_course.save()
                same_semester.append(selected_other_course)
            else:
                same_semester.extend(list(selected_other_course))
        
        selected_course.equivalent_courses.add(*equivalent_courses)
        selected_course.same_semester_courses.add(*same_semester)
        
        selected_course.save()
        
        semester_keys = PlanSemester.SEMESTER_CHOICES.keys()
        year_keys = PlanSemester.YEAR_IN_SCHOOL_CHOICES.keys()
        
        for semester_number in course_details['semesters']:
            year = (int(semester_number) // 10) - 1
            semester = int(semester_number) % 10
            
        selected_semester = PlanSemester.objects.filter(year=year_keys[year], semester=semester_keys[semester])
        if not selected_semester.exists():
            selected_semester = PlanSemester(
                year=year_keys[year], 
                semester=semester_keys[semester]
            )
        else:
            selected_semester = list(selected_semester)[0]
            
        selected_semester.courses.add(selected_course)
        selected_semester.save()
        ...
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
    for subject, courses in schedule.items():
        for course, details in courses.items():
            selected_course = Course.objects.filter(subject=subject, class_number=int(course))
            if not selected_course.exists():
                selected_course = Course(
                    subject = subject, 
                    class_number=int(course),
                    weight = int(course) // 1000
                )
            else:
                selected_course = list(selected_course)[0]
                
            selected_course.name = details["title"]
            credit_hours = details['sections'][next(iter(details['sections']))]["Credit Hours"]
            try:
                credit_hours = int(credit_hours)
            except:
                credit_hours = 1
            selected_course.credits = credit_hours
            selected_course.save()
            
            for section, section_details in details['sections'].items():
                if section_details['Location'] in ['Totally Online', 'To Be Announced']:
                    print(f"{section_details['Location']} - Skipping")
                    continue

                selected_section = Section.objects.filter(course=selected_course, section_number=int(section))
                if not selected_section.exists():
                    selected_section = Section(
                        course=selected_course, 
                        section_number=int(section)
                    ) 
                else:
                    selected_section = list(selected_section)[0]
                selected_section.section_id = int(section_details['Class Number'].split(" ")[0])
                selected_section.professor = section_details['Instructor']
                room_dict = re.search('(?P<building>.+)\s?(?P<room_number>[0-9]*)', section_details['Location'])
                # print(room_dict.group('building'))
                # print(room_dict.group('room_number'))
                if room_dict.group('room_number') == '':
                    room_number = 0
                else:
                    room_number = int(room_dict.group('room_number'))
        
                selected_room = Room.objects.filter(building = room_dict.group('building'), room_number = room_number)
                if not selected_room.exists():
                    selected_room = Room(
                        building = room_dict.group('building'), 
                        room_number = room_number,
                        capacity = int(section_details['Class Max'])
                    )
                else:
                    selected_room = list(selected_room)[0]
                
                selected_room.capacity = max(selected_room.capacity, int(section_details['Class Max']))
                selected_room.save()
                selected_section.room = selected_room
                # print(section_details['Time'])
                start_time, end_time = section_details['Time'].split(' - ')
                
                start_time = date.strptime(start_time, "%I:%M%p")
                end_time = date.strptime(end_time, "%I:%M%p")
                
                selected_section.start_time = start_time
                selected_section.end_time = end_time
                
                selected_section.save()
                for day in section_details['Days'].lower():
                    selected_day = Day.objects.get(day_of_week = Day.DAY_OF_WEEK_CHOICES[day])
                    selected_section.days.add(selected_day)
                
