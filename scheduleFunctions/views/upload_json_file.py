from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from ..models import FilteredUpload
from ..to_database import store_schedule, clear_schedule
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from datetime import datetime
import os

# Constants
SUBJECTS_OF_INTEREST = {"CIST", "CSCI"}
NON_CS_SUBJECTS_OF_INTEREST = {"ENGL", "MATH", "CMST"}
NON_CS_COURSES_OF_INTEREST = {
    "engl1150",
    "cmst1110",
    "cmst2120",
    "math1950",
    "engl1160",
    "math2050",
}

# === Convert filtered to ASP facts ===


##
# @brief Converts a 12-hour formatted time string to minutes past midnight.
#
# @param time A string in the format "%I:%M%p" (e.g., "03:45PM").
# @return Integer number of minutes since midnight.
def convert24(time):
    t = datetime.strptime(time, "%I:%M%p")
    return t.hour * 60 + t.minute


##
# @brief Converts a nested JSON schedule dictionary into ASP logic program facts.
#
# @param schedule_list A dictionary representing course schedule data.
# @return A list of strings, each representing a logic fact for use in ASP (Answer Set Programming).
def convert_json_to_lp(schedule_list):
    facts = []
    non_cs_classes, classes, rooms, professors, non_cs_times, times = (
        set(),
        set(),
        set(),
        set(),
        set(),
        set(),
    )
    for term, subjects in schedule_list.items():
        for subject, courses in subjects.items():
            for course_num, course_info in courses.items():
                course_id = (
                    f"{subject}{course_num}".lower()
                    .replace(" ", "_")
                    .replace(".", "")
                    .replace("-", "_")
                )
                if (
                    subject in NON_CS_SUBJECTS_OF_INTEREST
                    and course_id not in NON_CS_COURSES_OF_INTEREST
                ):
                    continue
                title = (
                    course_info.get("title", "")
                    .lower()
                    .replace(" ", "_")
                    .replace(".", "")
                    .replace("-", "_")
                )
                # prereq = (
                #     course_info.get("prereq", "none")
                #     .lower()
                #     .replace(" ", "_")
                #     .replace("-", "_")
                #     .replace(".", "")
                # )

                # keep track of  how many sections are totally online
                # if they are all totally online, skip the course
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
                    credits = section_info.get("Credit Hours")

                    if (
                        location in {"totally_online", "to_be_announced"}
                        or start == "tba"
                    ):
                        totally_online_count += 1
                        continue

                    # if we are a class that we can modify
                    if subject in SUBJECTS_OF_INTEREST:
                        facts.append(
                            f"section({course_id}, {section_num}, {class_number}, {start}, {end}, {days}, {location}, {instructor})."
                        )
                        rooms.add(location)
                        professors.add(instructor)
                        if start != "tba" and end != "tba" and days != "tba":
                            times.add(
                                f"time_slot_credits({start}, {end}, {days}, {credits})."
                            )
                    # else we are a class like english or math and we cannot modify the time
                    else:
                        facts.append(
                            f"non_cs_section({course_id}, {section_num}, {class_number}, {start}, {end}, {days}, {location}, {instructor})."
                        )
                        if start != "tba" and end != "tba" and days != "tba":
                            non_cs_times.add(
                                f"non_cs_time_slot({start}, {end}, {days})."
                            )

                # ignore courses that are entirely comprised of totally online sections
                if totally_online_count == section_count:
                    continue

                # if we are a class that we can modify
                if subject in SUBJECTS_OF_INTEREST:
                    # facts.append(f'course({course_id}, "{title}").')
                    # weight = 1
                    if str(course_num).startswith("1"):
                        year = 1
                    elif str(course_num).startswith("2"):
                        year = 2
                    elif str(course_num).startswith("3"):
                        year = 3
                    elif str(course_num).startswith("4"):
                        year = 4
                    elif str(course_num).startswith("8") or str(course_num).startswith(
                        "9"
                    ):
                        year = 5
                    else:
                        year = 0
                        print(
                            f"Error for course id: {course_id} with course number: {course_num}"
                        )
                    facts.append(f"course_year({course_id}, {year}).")
                    classes.add(course_id)
                # else we are a class like english or math and we cannot modify the time
                else:
                    # facts.append(f'non_cs_course({course_id}, "{title}").')
                    # weight = 1
                    if str(course_num).startswith("1"):
                        year = 1
                    elif str(course_num).startswith("2"):
                        year = 2
                    elif str(course_num).startswith("3"):
                        year = 3
                    elif str(course_num).startswith("4"):
                        year = 4
                    elif str(course_num).startswith("8") or str(course_num).startswith(
                        "9"
                    ):
                        year = 5
                    else:
                        year = 0
                        print(
                            f"Error for course id: {course_id} with course number: {course_num}"
                        )
                    facts.append(f"course_year({course_id}, {year}).")
                    non_cs_classes.add(course_id)

    facts.append(f"class({'; '.join(classes)}).")
    facts.append(f"non_cs_class({'; '.join(non_cs_classes)}).")
    facts.append(f"room({'; '.join(rooms)}).")
    facts.append(f"professor({'; '.join(professors)}).")
    facts.extend(times)
    facts.extend(non_cs_times)

    return facts


##
# @brief Handles uploading of a JSON file and its conversion to ASP logic facts.
#
# Accepts only POST requests. Saves raw, filtered, and non-filtered JSON data.
# Also converts filtered data into ASP facts and saves as `.lp` file.
#
# @param request Django HTTP request object.
# @return JsonResponse indicating success or error, with filenames of saved data.
@csrf_exempt
def upload_json_file(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return JsonResponse({"error": "No file provided"}, status=400)

    if not uploaded_file.name.lower().endswith(".json"):
        return JsonResponse({"error": "Only .json files are allowed"}, status=400)

    try:
        file_contents = uploaded_file.read()
        data = json.loads(file_contents)
        uploaded_file.seek(0)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

    if not data:
        return JsonResponse({"error": "Empty JSON file"}, status=400)

    # === Filtering ===
    latest_block = max(data.keys())
    filtered_courses = {latest_block: {}}
    non_filtered_courses = {latest_block: {}}

    for subject, courses in data[latest_block].items():
        if subject in SUBJECTS_OF_INTEREST or subject in NON_CS_SUBJECTS_OF_INTEREST:
            filtered_courses[latest_block][subject] = courses
        else:
            non_filtered_courses[latest_block][subject] = courses

    # === Save all three JSON versions ===
    upload_number = FilteredUpload.objects.count() + 1
    raw_filename = f"uploads/raw_input{upload_number}.json"
    filtered_filename = f"uploads/filtered_output{upload_number}.json"
    non_filtered_filename = f"uploads/remaining_output{upload_number}.json"

    default_storage.save(raw_filename, ContentFile(file_contents))
    default_storage.save(
        filtered_filename, ContentFile(json.dumps(filtered_courses, indent=2))
    )
    default_storage.save(
        non_filtered_filename, ContentFile(json.dumps(non_filtered_courses, indent=2))
    )
    clear_schedule()
    store_schedule(os.path.join(settings.BASE_DIR, "media", filtered_filename))
    # Save model
    record = FilteredUpload.objects.create(
        filename=f"raw_input{upload_number}.json",
        filtered_data=filtered_courses,
        non_filtered_data=non_filtered_courses,
        uploaded_file=uploaded_file,
    )

    facts = convert_json_to_lp(filtered_courses)

    asp_filename = raw_filename.replace(".json", ".lp")
    default_storage.save(asp_filename, ContentFile("\n".join(facts)))
    request.session["asp_filename"] = asp_filename
    return JsonResponse(
        {
            "message": f"Upload and conversion #{upload_number} complete.",
            "raw_file": raw_filename,
            "filtered_file": filtered_filename,
            "non_filtered_file": non_filtered_filename,
            "asp_file": asp_filename,
        }
    )
