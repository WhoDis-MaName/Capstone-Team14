import json
import os

def get_cist_csci_courses(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    subjects_of_interest = {"CIST", "CSCI"}
    filtered_courses = {}

    for term, subjects_dict in data.items():
        for subject_code, courses_dict in subjects_dict.items():
            if subject_code in subjects_of_interest:
                if term not in filtered_courses:
                    filtered_courses[term] = {}
                filtered_courses[term][subject_code] = courses_dict

    return filtered_courses
if __name__ == "__main__":
    if os.name == 'nt':
        current_directory = os.path.dirname(os.path.realpath(__file__)) # Get current directory
    else:
        current_directory = os.path.dirname(os.path.realpath(__name__)) # Get current directory
        

    path = current_directory.split(os.sep)

    root_index = path.index('scheduleFunctions')
    root_dir = os.sep.join(path[:root_index+1])
    data_dir = os.path.join(root_dir, 'data_files', 'uploaded_schedule')
    json_file =  os.path.join(data_dir, "fa21-fa24.json")
    
    result = get_cist_csci_courses(json_file)
    with open("filtered.json", "w", encoding='utf-8') as out:
        json.dump(result, out, indent=2)

    print("Filtered results have been written to filtered.json.")
