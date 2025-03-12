import json

def process_prereq(json_file_path: str) -> dict:
    """Take the json file that contains the current course schedule and process in place to read the prerequisites

    Args:
        json_file_path (str): file path to the json file containing the class list_

    Returns:
        dict: dictionary containing the processed data
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)


    for term, subjects_dict in data.items():
        for subject_code, courses_dict in subjects_dict.items():
            for course_code, course_definition in courses_dict.items():
                if course_definition['prereq'] == '-':
                    course_definition['prereq'] = []
                print(course_definition['prereq'])
                ...            
    return data


if __name__ == "__main__":
    json_file = "filtered.json"
    result = process_prereq(json_file)
    # with open("processed.json", "w", encoding='utf-8') as out:
    #     json.dump(result, out, indent=2)

    # print("Filtered results have been written to processed.json.")
