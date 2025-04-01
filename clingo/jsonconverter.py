import json
from datetime import datetime


## \brief Converts a 12-hour time format to minutes past midnight.
#  \param time A string representing time in the format "HH:MMAM/PM".
#  \return The number of minutes past midnight.
def convert24(time):
    t = datetime.strptime(time, "%I:%M%p")  # Parse the time string
    return t.hour * 60 + t.minute  # Convert to total minutes


## \brief Converts a JSON file containing course schedule information into ASP facts.
#  \param file The path to the JSON file containing the course data.
def convert(file):
    # Load the JSON data
    with open(file, "r") as f:
        data = json.load(f)

    # Initialize storage for facts and unique identifiers
    facts = []
    classes = set()
    rooms = set()
    professors = set()
    times = set()

    # Iterate through the JSON structure
    for term, subjects in data.items():
        for subject, courses in subjects.items():
            for course_num, course_info in courses.items():

                # Format course information
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

                    # Format section details
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

                    # Skip online or unconfirmed sections
                    if (
                        location in ["totally_online", "to_be_announced"]
                        or start == "tba"
                    ):
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

    # Convert sets to facts
    facts.append(f"class({'; '.join(classes)}).")
    facts.append(f"room({'; '.join(rooms)}).")
    facts.append(f"professor({'; '.join(professors)}).")
    facts.extend(times)  # Since times are already formatted as facts

    # Write ASP facts to a file
    asp_filename = file.replace(".json", ".lp")
    with open(asp_filename, "w") as f:
        f.write("\n".join(facts))
