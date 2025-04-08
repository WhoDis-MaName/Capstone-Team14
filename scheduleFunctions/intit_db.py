from data_processing import get_four_year, process_constraints
from models import *
import os

def init_plan(url, filename):
    # Storing four year plan as JSON file
    if not os.path.isfile(filename):
        get_four_year.read_four_year(url, filename)
    
    # Convert to rules
    constraints = process_constraints.create_constraints(filename)
    
    for key, value in constraints.items():
        course_object = Course.objects.filer(course_number__contains=key)
        ...
    
    ...
    
def init_requirements(filename):
    ...
    
def check_db_contents():
    print(Room.objects)
    print(Day.objects)
    print(Course.objects)
    print(Requirements_Group.objects)
    print(Schedule.objects)
    print(Section.objects)
    print(PlanSemester.objects)
    print(Change.objects)
    print(Conflict.objects)