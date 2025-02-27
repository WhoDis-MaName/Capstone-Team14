import json
import re

# Load JSON file
file_path = "filtered.json"
with open(file_path, "r") as file:
    data = json.load(file)


# Function to clean and format course codes
def format_course_code(department, course_number):
    return f"{department.lower()}_{course_number}"


# Function to parse prerequisites
def parse_prerequisites(prereq_text):
    prereqs = []

    # Common prerequisite formats
    course_pattern = re.findall(r"([A-Z]+)\s?(\d{4})", prereq_text)

    for dept, number in course_pattern:
        prereqs.append(format_course_code(dept, number))

    # Handle special cases
    if "permission of the instructor" in prereq_text.lower():
        prereqs.append("instructor_permission")

    return prereqs


# Extract courses and prerequisites
asp_facts = []

for term in data.values():
    for department, courses in term.items():
        for course_number, course in courses.items():
            course_code = format_course_code(department, course_number)
            title = course["title"].replace('"', "'")  # Ensure safe formatting

            asp_facts.append(f'course({course_code}, "{title}").')

            prereq_text = course.get("prereq", "").strip()
            if prereq_text and prereq_text != "-":
                for prereq in parse_prerequisites(prereq_text):
                    asp_facts.append(f"prereq({course_code}, {prereq}).")

# Save to a .lp file
output_file = "courses.lp"
with open(output_file, "w") as f:
    f.write("\n".join(asp_facts))

print(f"ASP facts saved to {output_file}")
