import json
from datetime import datetime


# Converting 12 hour time to minutes past midnight, ie: 12:15 AM to 15.
def convert24(time):
    t = datetime.strptime(time, "%I:%M%p")  # Parse the time string
    return t.hour * 60 + t.minute  # Convert to total minutes


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
                    f"{subject}{course_num}".lower()
                    .replace(" ", "_")
                    .replace(".", "")
                    .replace("-", "_")
                )
                title = (
                    course_info.get("title", "")
                    .lower()
                    .replace(" ", "_")
                    .replace(".", "")
                    .replace("-", "_")
                )
                prereq = (
                    course_info.get("prereq", "none")
                    .lower()
                    .replace(" ", "_")
                    .replace("-", "none")
                    .replace(".", "")
                    .replace("-", "_")
                )
                section_count = 0
                totally_online_count = 0
                for section_num, section_info in course_info.get(
                    "sections", {}
                ).items():
                    section_count += 1
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
                        .replace("-", "_")
                    )
                    location = (
                        section_info.get("Location", "Unknown")
                        .lower()
                        .replace(" ", "_")
                        .replace(".", "")
                        .replace("-", "_")
                    )
                    instructor = (
                        section_info.get("Instructor", "Unknown")
                        .lower()
                        .replace(" ", "_")
                        .replace(".", "")
                        .replace("-", "_")
                    )
                    if (
                        location == "totally_online"
                        or location == "to_be_announced"
                        or start == "tba"
                    ):
                        totally_online_count += 1
                        continue
                    # Store section fact
                    facts.append(
                        f"section({course_id}, {section_num}, {class_number}, {start}, {end}, {days}, {location}, {instructor})."
                    )

                    # Add to sets
                    rooms.add(location)
                    professors.add(instructor)
                    if start != "tba" and end != "tba" and days != "tba":
                        times.add(f"time_slot({start}, {end}, {days}).")
                if totally_online_count == section_count:
                    continue
                # Store course fact
                facts.append(f'course({course_id}, "{title}", {prereq}).')
                classes.add(course_id)

    # Convert sets to facts
    facts.append(f"class({'; '.join(classes)}).")
    facts.append(f"room({'; '.join(rooms)}).")
    facts.append(f"professor({'; '.join(professors)}).")
    facts.extend(times)  # Since times are already formatted as facts

    # Write ASP facts to a file
    asp_filename = file.replace(".json", ".lp")
    # asp_filename = "classes.lp"
    with open(asp_filename, "w") as f:
        f.write("\n".join(facts))

    # print(f"ASP facts written to {asp_filename}")


convert(
    r"C:\Users\cjgry\Documents\Capstone\Capstone-Team14\data_files\four_year_plan\filtered.json"
)
