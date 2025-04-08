import json
import re
import os

if os.name == 'nt':
    current_directory = os.path.dirname(os.path.realpath(__file__)) # Get current directory
else:
    current_directory = os.path.dirname(os.path.realpath(__name__)) # Get current directory
    

path = current_directory.split(os.sep)

root_index = path.index('scheduleFunctions')
root_dir = os.sep.join(path[:root_index+1])
data_dir = os.path.join(root_dir, 'data_files', 'uploaded_schedule')

try:
    os.makedirs(data_dir)
except:
    pass
# Load the JSON file
file_path = os.path.join(data_dir,"filtered.json")
with open(file_path, "r") as file:
    data = json.load(file)

# Dictionary to store parsed prerequisites
course_prereqs = {}

# Regular expressions to identify prerequisites
strict_prereq_pattern = re.compile(r"([\w\s]+) with C[-]? or better|([\w\s]+) AND|([\w\s]+) OR")

# Function to clean course names
def clean_course_name(course):
    return course.strip().replace(" ", "_").lower()

# Traverse the data structure
for term, subjects in data.items():
    for subject, courses in subjects.items():
        for course_number, course_info in courses.items():
            title = course_info.get("title", "Unknown Title")
            prereq_text = course_info.get("desc", "")

            # Extract prerequisites from the description
            if "Prereq:" in prereq_text:
                prereq_part = prereq_text.split("Prereq:")[1].strip()

                # Find all course mentions
                matches = strict_prereq_pattern.findall(prereq_part)
                all_prereqs = set()
                for match_group in matches:
                    for match in match_group:
                        if match:
                            all_prereqs.add(clean_course_name(match))

                # Handle "AND" vs "OR" conditions
                if "OR" in prereq_part:
                    structured_prereq = f"choice([{', '.join(all_prereqs)}])"
                else:
                    structured_prereq = ", ".join(all_prereqs)

                # Store results
                course_key = f"{clean_course_name(subject)}_{course_number}"
                course_prereqs[course_key] = structured_prereq

# Generate ASP facts
lp_file = os.path.join(root_dir,"courses.lp")
with open(lp_file, "w") as f:
    for course, prereq in course_prereqs.items():
        f.write(f"prereq({course}, {prereq}).\n")

print("ASP rules saved to courses.lp")
