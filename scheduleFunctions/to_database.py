import os
import json
import re
from datetime import datetime as date
from django.db.models import Count

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
            try:
                requirement = Requirement.objects.get(major_label=major_label, requirement_label=requirement_label)
            except Requirement.DoesNotExist:
                requirement = Requirement(
                    major_label = major_label,
                    requirement_label = requirement_label,
                    total_credits = data[major_label][requirement_label]['credits']
                )
                requirement.save()
                
            courses = data[major_label][requirement_label]['classes']
            course_list = []
            for course in courses:
                subject = course[:-4]
                course_number = int(course[-4:])
                try:
                    selected_course = Course.objects.get(subject = subject, class_number=course_number)
                except Course.DoesNotExist:
                    selected_course = Course(
                        subject = subject, 
                        class_number=course_number,
                        weight = course_number // 1000
                    )
                    selected_course.save()
                course_list.append(selected_course)                  
            requirement.course_options.add(*course_list)
                
                
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
        name = course_details['name']
        # print(course, name)
        course_number = int(course[-4:])
        
        try:
            selected_course = Course.objects.get(subject=subject, class_number=course_number) 
            selected_course.name = name
            selected_course = selected_course   
             
        except Course.DoesNotExist:
            selected_course = Course(
                name = name,
                subject = subject, 
                class_number=course_number,
                weight = course_number // 1000
            )
        finally:            
            selected_course.credits = int(course_details['credits'])
        
        equivalent_courses = []
        for other_course in course_details['equivalent_courses']:
            try:
                selected_other_course = Course.objects.get(
                    subject=other_course[:-4], 
                    class_number=int(other_course[-4:]))
            except Course.DoesNotExist:
                selected_other_course = Course(
                    subject=other_course[:-4], 
                    class_number=int(other_course[-4:]),
                    weight = int(other_course[-4:]) // 1000
                )
                selected_other_course.save()
                
            equivalent_courses.append(selected_other_course)
        
        same_semester = []
        for other_course in course_details['same_semester']:
            try:
                selected_other_course = Course.objects.get(
                    subject=other_course[:-4], 
                    class_number=int(other_course[-4:]))
            except Course.DoesNotExist:
                selected_other_course = Course(
                    subject=other_course[:-4], 
                    class_number=int(other_course[-4:]),
                    weight = int(other_course[-4:]) // 1000
                )
                selected_other_course.save()
            same_semester.append(selected_other_course)
        
        selected_course.save()
        selected_course.equivalent_courses.add(*equivalent_courses)
        selected_course.same_semester_courses.add(*same_semester)
        
        
        
        semester_keys = ["F","S"]
        year_keys = ["FR", "SO", "JR", "SR", "GR"]
        
        
        for semester_number in course_details['semesters']:
            year = (int(semester_number) // 10) - 1
            semester = int(semester_number) % 10
            
            
        try:
            selected_semester = PlanSemester.objects.get(year=year_keys[year], semester=semester_keys[semester])
        except PlanSemester.DoesNotExist:
            selected_semester = PlanSemester(
                year=year_keys[year], 
                semester=semester_keys[semester]
            )
        
        selected_semester.save()    
        selected_semester.courses.add(selected_course)
        
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
            try:
                selected_course = Course.objects.get(subject=subject, class_number=int(course))
            except Course.DoesNotExist:
                selected_course = Course(
                    subject = subject, 
                    class_number=int(course),
                    weight = int(course) // 1000
                )
                
            selected_course.name = details["title"]
            credit_hours = details['sections'][next(iter(details['sections']))]["Credit Hours"]
            try:
                credit_hours = int(credit_hours)
            except:
                credit_hours = 1
            selected_course.credits = credit_hours
            selected_course.save()
            
            for section, section_details in details['sections'].items():
                if section_details['Location'] in ['Totally Online', 'To Be Announced', 'Partially Online'] or section_details['Time'] == 'TBA':
                    # print(f"{section_details['Location']} - Skipping")
                    continue

                try:
                    selected_section = Section.objects.get(course=selected_course, section_number=int(section))
                except Section.DoesNotExist:
                    selected_section = Section(
                        course=selected_course, 
                        section_number=int(section)
                    ) 
                
                selected_section.section_id = int(section_details['Class Number'].split(" ")[0])
                
                try:
                    selected_professor = Proffessor.objects.get(name = section_details['Instructor'])
                except Proffessor.DoesNotExist:
                    selected_professor = Proffessor(
                        name = section_details['Instructor']
                        ) 
                    selected_professor.save()
                
                selected_section.professor = selected_professor
                room_dict = re.search('(?P<building>.+)\s?(?P<room_number>[0-9]*)', section_details['Location'])
                # print(room_dict.group('building'))
                # print(room_dict.group('room_number'))
                if room_dict.group('room_number') == '':
                    room_number = 0
                else:
                    room_number = int(room_dict.group('room_number'))
                    
                    
                try:
                    selected_room = Room.objects.get(building = room_dict.group('building'), room_number = room_number)
                except Room.DoesNotExist:
                    selected_room = Room(
                        building = room_dict.group('building'), 
                        room_number = room_number,
                        capacity = int(section_details['Class Max'])
                    )
                    selected_room.save()
                
                selected_room.capacity = max(selected_room.capacity, int(section_details['Class Max']))
                selected_room.save()
                selected_section.room = selected_room
                
                try:
                    start_time, end_time = section_details['Time'].split(' - ')
                    
                except ValueError as e:
                    print(section_details['Time'], '-', subject, course, section)
                    raise e
                    start_time, end_time = (None, None)
                
                start_time = date.strptime(start_time, "%I:%M%p")
                end_time = date.strptime(end_time, "%I:%M%p")
                
                selected_days = Day.objects.filter(day_of_week__in = [Day.DAY_OF_WEEK_CHOICES[day] for day in section_details['Days'].lower()])

                try:
                    selected_time = TimeSlot.objects.annotate(
                        num_days=Count('days')
                    ).filter(
                        days__in = selected_days
                    ).filter(
                        num_days=len(selected_days)
                    ).filter(
                        start_time = start_time,
                        end_time = end_time
                    ).distinct().get()
                except TimeSlot.DoesNotExist:
                    selected_time = TimeSlot(
                        start_time = start_time, 
                        end_time = end_time,
                        credits = credit_hours
                    )
                    selected_time.save()
                    for day in selected_days:
                        selected_time.days.add(day)
                    selected_time.save()
                except TimeSlot.MultipleObjectsReturned:
                    timeslots = TimeSlot.objects.annotate(
                        num_days=Count('days')
                    ).filter(
                        days__in = selected_days
                    ).filter(
                        num_days=len(selected_days)
                    ).distinct()
                    # for time in timeslots:
                        # print(time.print_clingo())
                selected_section.time_slot = selected_time
                selected_section.save()

def store_schedule_changes(section_id: int, start_time: date, end_time: date, days: str) -> None:
    print(section_id, start_time, end_time, days)
    try:
        selected_section = Section.objects.get(section_id=section_id)
    except Section.DoesNotExist:
        print(f"Something went wrong, section does not exist: {section_id}")

    try:
        selected_days = Day.objects.filter(day_of_week__in = [Day.DAY_OF_WEEK_CHOICES[day] for day in days])
        updated_time = TimeSlot.objects.annotate(
                        num_days=Count('days')
                    ).filter(
                        days__in = selected_days
                    ).filter(
                        num_days=len(days)
                    ).filter(
                        start_time = start_time,
                        end_time = end_time
                    ).distinct().get()
        
    except TimeSlot.DoesNotExist:
        updated_time = TimeSlot(
            start_time = start_time, 
            end_time = end_time,
            credits = selected_section.course.credits
        )
        updated_time.save()
        for day in selected_days:
            updated_time.days.add(day)
        updated_time.save()
        print(f"Something went wrong, timeslot doesn't exist: {(start_time, end_time, days)}")
        
    selected_section.time_slot = updated_time
    selected_section.changed = True
    selected_section.save()
   
def clear_schedule():
    Section.objects.all().delete()
    Room.objects.all().delete()
    Proffessor.objects.all().delete()
    TimeSlot.objects.all().delete()
    