import json
from datetime import datetime


# TODO - updated to encode facts in non-string representation
# ex: "CIST1400" -> cist1400, "MW" -> mw


# From: https://www.geeksforgeeks.org/python-program-convert-time-12-hour-24-hour-format/
def convert24(time):
    # Parse the time string into a datetime object
    t = datetime.strptime(time, "%I:%M%p")
    # Format the datetime object into a 24-hour time string
    return t.strftime("%H%M")


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
            course_id = f"{subject}{course_num}".lower().replace(" ", "-")
            classes_str += f'"{course_id}", '
            title = course_info.get("title", "").lower().replace(" ", "-")
            # there is a prereq field, but it seems like it is not filled out.
            # instead the prereq is inside of the description.
            prereq = course_info.get("prereq", "none").lower().replace(" ", "-")

            # Add course fact
            facts.append(f"course({course_id}, {title}, {prereq}).")

            for section_num, section_info in course_info.get("sections", {}).items():
                class_number = (
                    section_info.get("Class Number", "")
                    .split()[0]
                    .lower()
                    .replace(" ", "-")
                )

                # Get start and end time and convert to 24 hour format
                time = section_info.get("Time", "TBA")
                if time == "TBA":
                    start, end = "tba", "tba"
                else:
                    start, end = time.split(" - ")
                    start = convert24(start)
                    end = convert24(end)

                days = section_info.get("Days", "TBA").strip().lower()
                location = section_info.get("Location", "Unknown").lower()
                instructor = (
                    section_info.get("Instructor", "Unknown").lower().replace(" ", "-")
                )

                rooms_set.add(f'"{location}"')
                professors_set.add(f'"{instructor}"')

                times_set.add(f"({time}, {days})")

                # Add section fact
                facts.append(
                    f"section({course_id.lower()}, {section_num.lower()}, {class_number.lower()}, {start.lower()}, {end.lower()}, {days.lower()}, {location.lower()}, {instructor.lower()})."
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
