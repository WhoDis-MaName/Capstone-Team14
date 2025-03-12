import json
from datetime import datetime


# Convert 12-hour time format to 24-hour format
# TODO: Update to encode minutes past midnight instead of converting 12:15 AM to 0115, convert to 15.
def convert24(time):
    t = datetime.strptime(time, "%I:%M%p")  # Parse the time string
    return t.strftime("%H%M")  # Format it into 24-hour format


def convert(file):

    # Load the JSON data
    with open(file, "r") as f:
        data = json.load(f)

    # Extract course information
    facts = []

    classes = set()
    rooms = set()
    professors = set()
    times = set()

    for term, subjects in data.items():
        for subject, courses in subjects.items():
            for course_num, course_info in courses.items():
                course_id = (
                    f"{subject}{course_num}".lower().replace(" ", "_").replace(".", "")
                )
                title = (
                    course_info.get("title", "")
                    .lower()
                    .replace(" ", "_")
                    .replace(".", "")
                )
                prereq = (
                    course_info.get("prereq", "none")
                    .lower()
                    .replace(" ", "_")
                    .replace("-", "none")
                    .replace(".", "")
                )

                # Store course fact
                facts.append(f'course({course_id}, "{title}", {prereq}).')
                classes.add(course_id)

                for section_num, section_info in course_info.get(
                    "sections", {}
                ).items():
                    section_num = "s" + section_num.lower()
                    class_number = (
                        "c" + section_info.get("Class Number", "").split()[0].lower()
                    )

                    # Convert time to 24-hour format
                    time = section_info.get("Time", "TBA")
                    if time == "TBA":
                        start, end = "tba", "tba"
                    else:
                        start, end = time.split(" - ")
                        start = convert24(start)
                        end = convert24(end)

                    days = (
                        section_info.get("Days", "TBA")
                        .strip()
                        .lower()
                        .replace(" ", "_")
                    )
                    location = (
                        section_info.get("Location", "Unknown")
                        .lower()
                        .replace(" ", "_")
                        .replace(".", "")
                    )
                    instructor = (
                        section_info.get("Instructor", "Unknown")
                        .lower()
                        .replace(" ", "_")
                        .replace(".", "")
                    )

                    # Store section fact
                    facts.append(
                        f'section({course_id}, {section_num}, {class_number}, "{start}", "{end}", {days}, {location}, {instructor}).'
                    )

                    # Add to sets
                    rooms.add(location)
                    professors.add(instructor)
                    times.add(f'time_slot("{start}", "{end}", {days}).')

    # Convert sets to facts
    facts.append(f"class({', '.join(classes)}).")
    facts.append(f"room({', '.join(rooms)}).")
    facts.append(f"professor({', '.join(professors)}).")
    facts.extend(times)  # Since times are already formatted as facts

    # Write ASP facts to a file
    asp_filename = file.replace(".json", ".lp")
    # asp_filename = "classes.lp"
    with open(asp_filename, "w") as f:
        f.write("\n".join(facts))

    # print(f"ASP facts written to {asp_filename}")
