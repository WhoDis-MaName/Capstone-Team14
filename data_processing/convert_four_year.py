import json


def json_to_clingo(json_file, output_file):
    with open(json_file, "r") as file:
        data = json.load(file)

    # If the JSON root is a list, assume it contains a dictionary
    if isinstance(data, list) and len(data) > 0:
        data = data[0]  # Take the first element

    if not isinstance(data, dict):
        raise ValueError(
            "Invalid JSON structure: Expected a dictionary at the top level."
        )

    clingo_facts = []

    year_id = 1
    module_id = 0
    for year, semesters in data.items():
        year_fact = f"year({year_id})."
        clingo_facts.append(year_fact)

        for semester, courses in semesters.items():
            for course_group in courses:
                course_codes, course_names, credits = course_group

                module_fact = f"module(m{module_id}, {year_id})."
                clingo_facts.append(module_fact)

                for course in course_codes:
                    course_fact = f"course({course}, m{module_id}, {credits})."
                    clingo_facts.append(course_fact)

                module_id += 1
        year_id += 1

    with open(output_file, "w") as file:
        file.write("\n".join(clingo_facts))


# Example usage
json_file = r"C:\Users\cjgry\Documents\Capstone\Capstone-Team14\data_files\four_year_plan\fourYearPlan.json"  # Change this to your actual file path
output_file = json_file.replace(".json", ".lp")  # Output file
json_to_clingo(json_file, output_file)
