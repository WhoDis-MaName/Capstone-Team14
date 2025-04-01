import json

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
    json_file = "fa21-fa24.json"
    result = get_cist_csci_courses(json_file)
    with open("filtered.json", "w", encoding='utf-8') as out:
        json.dump(result, out, indent=2)

    print("Filtered results have been written to filtered.json.")
