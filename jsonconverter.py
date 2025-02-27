import json

# Load the JSON data
with open("filtered.json", "r") as f:
    data = json.load(f)

# Extract course information
facts = []
classes = ""

for term, subjects in data.items():
    for subject, courses in subjects.items():
        for course_num, course_info in courses.items():
            course_id = f"{subject}{course_num}"
            classes += f'"{course_id}", '
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

                # Add section fact
                facts.append(
                    f'section("{course_id}", "{section_num}", "{class_number}", "{time}", "{days}", "{location}", "{instructor}").'
                )

facts.append(f"classes({classes[:-2]})")
# Write ASP facts to a file
asp_filename = "classes.lp"
with open(asp_filename, "w") as f:
    f.write("\n".join(facts))

print(f"ASP facts written to {asp_filename}")
