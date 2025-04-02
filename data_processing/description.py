import json
import os

if os.name == 'nt':
    current_directory = os.path.dirname(os.path.realpath(__file__)) # Get current directory
else:
    current_directory = os.path.dirname(os.path.realpath(__name__)) # Get current directory
    

path = current_directory.split(os.sep)

root_index = path.index('Capstone-Team14')
root_dir = os.sep.join(path[:root_index+1])
data_dir = os.path.join(root_dir, 'data_files', 'uploaded_schedule')

try:
    os.makedirs(data_dir)
except:
    pass

# Load the JSON file

file_path = os.path.join(data_dir, "filtered.json")
with open(file_path, "r") as file:
    data = json.load(file)

# Dictionary to store course prerequisites
course_prerequisites = {}

# Traverse the data structure
for term, subjects in data.items():
    for subject, courses in subjects.items():
        for course_number, course_info in courses.items():
            title = course_info.get("title", "Unknown Title")
            prereq_text = course_info.get("desc", "")

            # Extract prerequisites from the description
            if "Prereq:" in prereq_text:
                prereq_part = prereq_text.split("Prereq:")[1].strip()
                course_prerequisites[f"{subject} {course_number} - {title}"] = prereq_part

# Print prerequisites in a structured format
for course, prereq in course_prerequisites.items():
    print(f"{course} -> {prereq}")
