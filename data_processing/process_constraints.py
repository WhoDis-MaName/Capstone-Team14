import os
import json
from pprint import pprint

if os.name == 'nt':
    current_directory = os.path.dirname(os.path.realpath(__file__)) # Get current directory
else:
    current_directory = os.path.dirname(os.path.realpath(__name__)) # Get current directory
    

path = current_directory.split(os.sep)

root_index = path.index('Capstone-Team14')
root_dir = os.sep.join(path[:root_index+1])
data_dir = os.path.join(root_dir, 'data', 'four_year_plan')

def get_plan(filename: str) -> list[dict]:
    with open(filename, 'r') as file:
        data = json.load(file)
    if type(data) != list:
        raise SyntaxError("Read file is not in the expected format")
    return data
    ...
    
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
        ...
        
    return semester_content
    ...
    
def set_contsraints(semester_plan: list, semester_id: int) -> dict:
    """Process the semester such that classes listed as fulfilling the same requirement are soft constraints and all other classes in the semester are hard constraints

    Args:
        semester_plan (list): list of classes in the same semester in the same structure as the origional four year plan

    Returns:
        dict: Dictionary containing all of the classes in the semester
            - Structure:
                <course number like csci2040>: {
                    'equivalent_courses': set,
                    'same_semester': set,
                    'credits': int,
                    'semsesters': set
                }
    """
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
        
        ...
    
    # Set hard constraints as every class in semester not in soft constraints
    for course in semester_dict.keys():
        semester_dict[course]['same_semester'] = {x for x in classes_in_semester if x != course and x not in semester_dict[course]['equivalent_courses']}
    return semester_dict
    ...
    
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
    
    
def create_constraints(filename: str):
    
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
    
def convert_asp(constraints, file):
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
        ...
    ...

if __name__ == "__main__":
    filename = os.path.join(data_dir, 'fourYearPlan.json')
    constraints = create_constraints(filename)
    json_file = os.path.join(data_dir, 'constraints.json')
    asp_file = os.path.join(data_dir, 'four_year_plan_constraints.lp')
    
    with open(json_file, 'w') as f:
        json.dump(constraints,f, indent=4)
    
    with open(asp_file, 'w') as f:
        convert_asp(constraints, f)
    # pprint(constraints)
    