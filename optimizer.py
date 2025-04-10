import sys, clingo, math
import argparse
import os
import json
import re

if os.name == "nt":
    current_directory = os.path.dirname(
        os.path.realpath(__file__)
    )  # Get current directory
else:
    current_directory = os.path.dirname(
        os.path.realpath(__name__)
    )  # Get current directory
path = current_directory.split(os.sep)

root_index = path.index("Capstone-Team14")
root_dir = os.sep.join(path[: root_index + 1])
read_dir = os.path.join(root_dir, "data_files", "uploaded_schedule")


# TODO: add in doxygen comments for clingo application.
class ClingoApp(clingo.application.Application):
    def main(self, ctl, files):
        ctl.load(root_dir + "\clingo\overlap_minimizer.lp")

        ctl.ground()
        ctl.solve()

    # TODO: update print model to print out the scheduled sections and parse into a json like filtered.json and upload back to the website to be displayed
    def print_model(self, model, printer) -> None:
        symbols = [str(s) for s in list(model.symbols(shown=True))]
        print(symbols)

        convert_to_json(symbols, "media\output.json")


def parse_line(line):
    # Extract the contents inside scheduled_section(...)
    match = re.match(r"scheduled_section\((.*?)\)", line.strip())
    if not match:
        return None

    fields = match.group(1).split(",")
    if len(fields) != 8:
        return None

    subject_course, section, class_number, start, end, days, location, instructor = (
        fields
    )
    subject = subject_course[:4].upper()
    course_number = subject_course[4:]

    section = section[1:]  # remove leading 's' from section number
    class_number = class_number[1:]  # remove leading 'c'

    # Convert start and end time to a readable format
    def convert_time(t):
        t = int(t)
        hours = t // 60
        minutes = t % 60
        suffix = "AM" if hours < 12 else "PM"
        hours = hours if hours <= 12 else hours - 12
        return f"{hours}:{minutes:02d}{suffix}"

    time_str = f"{convert_time(start)} - {convert_time(end)}"

    section_data = {
        "Class Number": class_number,
        "Date": "Aug 26, 2024 - Dec 20, 2024",
        "Time": time_str,
        "Days": days.upper(),
        "Location": location.replace("_", " ").title(),
        "Instructor": instructor.replace("_", " ").title(),
    }

    return subject, course_number, section, section_data


def convert_to_json(symbols, output_file):
    data = {}

    for line in symbols:
        parsed = parse_line(line)
        if not parsed:
            continue
        subject, course_number, section, section_data = parsed

        if subject not in data:
            data[subject] = {}

        if course_number not in data[subject]:
            data[subject][course_number] = {
                "title": "TBD",
                "desc": "TBD",
                "prereq": "-",
                "sections": {},
            }

        data[subject][course_number]["sections"][section] = section_data

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)


clingo.application.clingo_main(ClingoApp())
