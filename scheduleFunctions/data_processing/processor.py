import json
import os

def get_cist_csci_courses(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Find the most recent block
    latest_block = max(data.keys())
    subjects_of_interest = {"CIST", "CSCI"}
    filtered_courses = {}

    # Only process the latest block
    latest_subjects = data[latest_block]
    for subject_code, courses_dict in latest_subjects.items():
        if subject_code in subjects_of_interest:
            if latest_block not in filtered_courses:
                filtered_courses[latest_block] = {}
            filtered_courses[latest_block][subject_code] = courses_dict

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
