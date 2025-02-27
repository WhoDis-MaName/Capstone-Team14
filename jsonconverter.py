import json

# Load the JSON data
with open("filtered.json", "r") as f:
    data = json.load(f)

# Extract course information
facts = []


classes_str = ""
rooms_str = ""
professors_str = ""
times_str = ""


# classes_set = set()
rooms_set = set()
professors_set = set()
times_set = set()

for term, subjects in data.items():
    for subject, courses in subjects.items():
        for course_num, course_info in courses.items():
            course_id = f"{subject}{course_num}"
            classes_str += f'"{course_id}", '
            title = course_info.get("title", "")
            # there is a prereq field, but it seems like it is not filled out.
            # instead the prereq is inside of the description.
            prereq = course_info.get("prereq", "-")

            # Add course fact
            facts.append(f'course("{course_id}", "{title}", "{prereq}").')

            for section_num, section_info in course_info.get("sections", {}).items():
                class_number = section_info.get("Class Number", "").split()[0]
                time = section_info.get("Time", "TBA")
                days = section_info.get("Days", "TBA").strip()
                location = section_info.get("Location", "Unknown")
                instructor = section_info.get("Instructor", "Unknown")

                rooms_set.add(f'"{location}"')
                professors_set.add(f'"{instructor}"')
                times_set.add(f'("{time}", "{days}")')

                # Add section fact
                facts.append(
                    f'section("{course_id}", "{section_num}", "{class_number}", "{time}", "{days}", "{location}", "{instructor}").'
                )

for room in rooms_set:
    rooms_str += room + ", "

for professor in professors_set:
    professors_str += professor + ", "

for time in times_set:
    times_str += time + ", "


# Add list of all items
facts.append(f"class({classes_str[:-2]}).")
facts.append(f"room({rooms_str[:-2]}).")
facts.append(f"professor({professors_str[:-2]}).")
facts.append(f"time({times_str[:-2]}).")

# Write ASP facts to a file
asp_filename = "classes.lp"
with open(asp_filename, "w") as f:
    f.write("\n".join(facts))

print(f"ASP facts written to {asp_filename}")
