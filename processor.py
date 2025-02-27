import json

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
    json_file = "fa21-fa24.json"
    result = get_cist_csci_courses(json_file)
    with open("filtered.json", "w", encoding='utf-8') as out:
        json.dump(result, out, indent=2)

    print("Filtered results have been written to filtered.json.")
