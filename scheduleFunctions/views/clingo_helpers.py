from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import multiprocessing
import clingo
import re
import json
import os


# === Utility Functions ===

##
# @brief Returns the root path of the project by finding the 'Capstone-Team14' directory in the path.
# @return The absolute path to the root project directory.
def get_root_path():
    path = os.path.dirname(os.path.realpath(__file__)).split(os.sep)
    root_index = path.index("Capstone-Team14")
    return os.sep.join(path[: root_index + 1])

##
# @brief Loads and parses a JSON file from the specified path.
# @param path The path to the JSON file.
# @return The deserialized Python object (dict or list).
def load_optimized_json(path):
    with open(path, "r") as f:
        return json.load(f)


# === JSON Conversion Functions ===

##
# @brief Converts a time in minutes to a human-readable 12-hour clock format with AM/PM.
# @param t The time in minutes.
# @return A string representation of the time (e.g., "9:30AM").
def convert_time(t):
    t = int(t)
    hours = t // 60
    minutes = t % 60
    suffix = "AM" if hours < 12 else "PM"
    hours = hours if hours <= 12 else hours - 12
    return f"{hours}:{minutes:02d}{suffix}"

##
# @brief Parses a single line of ASP output representing a scheduled section.
# @param line A string line containing an ASP predicate like `scheduled_section(...)`.
# @return A tuple with subject, course number, section, and a dictionary of schedule data, or None if parsing fails.
def parse_line(line):
    match = re.match(r"scheduled_section\((.*?)\)", line.strip())
    if not match:
        return None
    fields = match.group(1).split(",")
    if len(fields) != 8:
        return None
    (
        subject_course,
        section,
        class_number,
        start,
        end,
        days,
        location,
        instructor,
    ) = fields
    subject = subject_course[:4].upper()
    course_number = subject_course[4:]
    section = section[1:]
    class_number = class_number[1:]
    time_str = f"{convert_time(start)} - {convert_time(end)}"
    return (
        subject,
        course_number,
        section,
        {
            "Class Number": class_number,
            "Date": "Aug 26, 2024 - Dec 20, 2024",
            "Time": time_str,
            "Days": days.upper(),
            "Location": location.replace("_", " ").title(),
            "Instructor": instructor.replace("_", " ").title(),
        },
    )

##
# @brief Converts a list of ASP symbols to a structured JSON file.
# @param symbols A list of ASP symbol strings (e.g., from Clingo models).
# @param output_file The path where the JSON output should be saved.
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

##
# @brief Runs Clingo on the given ASP program and minimizer, using all available threads.
# @param asp_filename The filename of the main ASP input file (in /media).
# @param asp_solver The filename of the minimizer or secondary ASP file (in /clingo).
# @return A list of shown symbols from the last (optimal) model found by Clingo.
def run_clingo_optimization(asp_filename, asp_solver):
    root_dir = get_root_path()
    asp_path = os.path.join(root_dir, "media", asp_filename)
    minimizer_path = os.path.join(root_dir, "clingo", asp_solver)

    available_threads = multiprocessing.cpu_count()

    print(f"Available threads on machine: {available_threads}")

    ctl = clingo.Control(["-t", str(available_threads)])
    ctl.load(asp_path)
    ctl.load(minimizer_path)
    ctl.ground()

    last_model_symbols = []

    def on_model(model):
        shown_symbols = model.symbols(shown=True)
        print("New model (potentially better):")
        for sym in shown_symbols:
            print(str(sym))
        # Overwrite with the current (better) model
        last_model_symbols.clear()
        last_model_symbols.extend(str(sym) for sym in shown_symbols)

    ctl.solve(on_model=on_model)

    return last_model_symbols

##
# @brief Saves a Python dictionary as a formatted JSON file using Django's storage system.
# @param data The data to be saved.
# @param filename The filename to save to (relative to Django's media path).
# @return The final path where the file was saved.
def save_optimized_file(data, filename):
    return default_storage.save(filename, ContentFile(json.dumps(data, indent=2)))
