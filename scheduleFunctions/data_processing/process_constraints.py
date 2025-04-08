## @package process_constraints
#  This module contains all of the functionality that is needed to convert the four year plan into usable clingo rules. 
#
#  For proof of concept running this package as a script utilizes the Computer Science four year plan.
import os
import json
from pprint import pprint

## Read the four year plan from a file and confirm that it is a list
# 
# @param filename 
# \parblock
# A string that contains the file path and filename that the JSON will be written to. 
# 
# *NOTE* to maintain the script's OS agnostic nature, 
# it is suggested to utilize os.path.join() to join strings or os.sep.join() to join elements of a list
# \endparblock 
# @return The list of dictionaries that was read from the file.
def get_plan(filename: str) -> list[dict]:
    with open(filename, 'r') as file:
        data = json.load(file)
    if type(data) != list:
        raise SyntaxError("Read file is not in the expected format")
    return data
    
## Get the list of classes for a particular semester from the four year plan, assuming that there may be multiple plans given
#
# @param plan 
# \parblock
# A list of dictionaries. Each dictionary defines a four year plan such that it has this structure
#
# {
#   'year':{
#       'semsester':[
#                       [ list of class numbers],
#                       [ list of class names],
#                       number of credits filled by the class(es) in the list
#                   ]
#       ...
#   }
# ...   
# }
# 
# \endparblock
#
# @param year 
# \parblock
# A string or an integer to identify the year in the plan that is to be read from. 
# Options: ['First Year', 'Second Year', 'Third Year', 'Fourth Year'] or [1, 2, 3, 4]
# \endparblock
# 
# @param semester
# \parblock
# A string that determines if fall semester or spring semester
# Options: ['FALL', 'SPRING'] or any variation in capitalization
# \endparblock
#
# @return A list of classes in the same structure as origional semester list combined for all plans in the origional list.
def get_semester(plan: list[dict], year: str|int, semester: str ) -> list:
    years = ['First Year', 'Second Year', 'Third Year', 'Fourth Year']
    if type(year) == str:
        year = year.upper()
        if year not in years:
            raise ValueError("Provided year not 'First Year', 'Second Year', 'Third Year', or 'Fourth Year'")
    elif type(year) == int:
        if year > 4 or year < 1:
            raise ValueError("Provided year outside range of 1-4 ")
        year = years[year-1]
    else:
        raise TypeError(f"Provided year of type {type(year)}, not str or int")
        
    semester = semester.upper()
    if semester not in ['FALL', 'SPRING']:
        raise ValueError("Provided semester not FALL or SPRING")
        
    semester_content = []
    
    for sub_plan in plan:
        semester_content.extend(sub_plan[year][semester])
        
        
    return semester_content
    
 
## Process the semester such that classes listed as fulfilling the same requirement are soft constraints and all other classes in the semester are hard constraints.
# 
# @param semester_plan list of classes in the same semester in the same structure as the origional four year plan
#
# @return
# \parblock
# Dictionary containing all of the classes in the semester
# Structure:
#    <course number like csci2040>: {
#       'equivalent_courses': set,
#       'same_semester': set,
#       'credits': int,
#       'semsesters': set
#    }
#   ...
# \endparblock 
def set_contsraints(semester_plan: list, semester_id: int) -> dict:
    
    semester_dict = {}
    classes_in_semester = set([])
    for course_group in semester_plan:
        # Confirm structure of each course group
        if len(course_group) != 3:
            raise SyntaxError("Read file is not in the expected format")          
            
        # Set constraint structure for each course
        for course in course_group[0]:
            
            semester_dict[course] = {
                'equivalent_courses': set([x for x in course_group[0] if x != course]),
                'same_semester': set([]),
                'credits': course_group[2],
                'semesters': {semester_id}
            }
        classes_in_semester.update(course_group[0])

    
    # Set hard constraints as every class in semester not in soft constraints
    for course in semester_dict.keys():
        semester_dict[course]['same_semester'] = {x for x in classes_in_semester if x != course and x not in semester_dict[course]['equivalent_courses']}
    return semester_dict
    

## Combine the constraints so that the keys are based on the course and not based on the semester
#
# @param constraints A list where each item in the list represents the classes in a semester
# @return A dictionary whose keys are all of the classes described in the four year plan
def combine_constraints(constraints: list[dict]) -> dict:
    complete_constraints = {}
    
    for semsester in constraints:
        for key, value in semsester.items():
            if key in complete_constraints.keys():
                complete_constraints[key]['same_semester'].update(value['same_semester'])
                complete_constraints[key]['equivalent_courses'].update(value['equivalent_courses'])
                complete_constraints[key]['semesters'].update(value['semesters'])
            else:
                complete_constraints[key] = value
                
    return complete_constraints
    
## Take a four year plan stored in a JSON file and process it so that it can be stored as JSON or as clingo in the desired format
#
# @param filename 
# \parblock
# A string that contains the file path and filename that the JSON will be written to. 
# 
# *NOTE* to maintain the script's OS agnostic nature, 
# it is suggested to utilize os.path.join() to join strings or os.sep.join() to join elements of a list
# \endparblock 
# @return A dictionary whose keys are all of the courses in the four year plan
def create_constraints(filename: str) -> dict:
    
    plan = get_plan(filename)
    semesters = ['fall', 'spring']
    constraint_list = []
    for year in range(1,5):
       for i in range(0,2):
           semester_plan = get_semester(plan, year, semesters[i]) 
           constraint_list.append(set_contsraints(semester_plan, year*10 + i))
    # pprint(constraint_list)
    constraints = combine_constraints(constraint_list)
    
    for key in constraints.keys():
        constraints[key]['same_semester'] = list(constraints[key]['same_semester'])
        constraints[key]['equivalent_courses'] = list(constraints[key]['equivalent_courses'])
        constraints[key]['semesters'] = list(constraints[key]['semesters'])
        
    return constraints

## Take formated constraints and convert it into asp rules
# In addition to the rules defined by the constraints parameter, the rules file is also appended with equivalence rules.
# \f$ a \equiv c \Leftarrow a \equiv b, b \equiv c \f$
# \f$ b \in S \Leftarrow a \in S, a \equiv b \f$
# * etc.
#
# @param constraints 
# @param file
# \parblock
# A string that contains the file path and filename that the JSON will be written to. 
# 
# *NOTE* to maintain the script's OS agnostic nature, 
# it is suggested to utilize os.path.join() to join strings or os.sep.join() to join elements of a list
# \endparblock     
def convert_asp(constraints: dict, file: str) -> None:
    for course in constraints.keys():
        # Equivalent classes
        for other in constraints[course]['same_semester']:
            file.write(f'same_semester({course}, {other}).\n')
        
        # Same Semester classes
        for other in constraints[course]['equivalent_courses']:
            file.write(f'equivalent_courses({course}, {other}).\n')
        
        # Class in Semester
        for semester in constraints[course]['semesters']:
            file.write(f'course_in_semester({semester}, {course}).\n')
            
    # Predetermined Rules
    file.write('equivalent_courses(C1, C3) :- equivalent_courses(C1, C2), equivalent_courses(C2, C3).\n')
    file.write('course_in_semester(S1, C2) :- equivalent_courses(C1, C2), course_in_semester(S1, C1).\n')
    file.write('same_semester(C1, C3) :- same_semester(C1, C2), same_semester(C2, C3).\n')
    file.write('same_semester(C1, C3) :- equivalent_courses(C1, C2), same_semester(C2, C3).\n')

if __name__ == "__main__":
    if os.name == 'nt':
        current_directory = os.path.dirname(os.path.realpath(__file__)) # Get current directory
    else:
        current_directory = os.path.dirname(os.path.realpath(__name__)) # Get current directory
        

    path = current_directory.split(os.sep)

    root_index = path.index('scheduleFunctions')
    root_dir = os.sep.join(path[:root_index+1])
    data_dir = os.path.join(root_dir, 'data_files', 'four_year_plan')
    filename = os.path.join(data_dir, 'fourYearPlan.json')
    constraints = create_constraints(filename)
    json_file = os.path.join(data_dir, 'constraints.json')
    asp_file = os.path.join(data_dir, 'four_year_plan_constraints.lp')
    
    with open(json_file, 'w') as f:
        json.dump(constraints,f, indent=4)
    
    with open(asp_file, 'w') as f:
        convert_asp(constraints, f)
    # pprint(constraints)
    