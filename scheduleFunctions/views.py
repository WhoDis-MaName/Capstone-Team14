from datetime import datetime
import os
import subprocess
import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile  # <-- Add this line
from django.core.files.storage import default_storage
from django.utils.timezone import now
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from .models import *
from scheduleFunctions.data_processing.jsonconverter import convert
from scheduleFunctions.data_processing.get_requirements import *
from scheduleFunctions.to_database import store_schedule
from scheduleFunctions.data_processing.optimizer import *



def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        

        # Get the absolute path to users.txt
        current_dir = os.path.dirname(os.path.abspath(__file__))
        users_file_path = os.path.join(current_dir, "users.txt")

        try:
            # Read users.txt
            with open(users_file_path, "r") as file:
                users = [line.strip().split(",") for line in file.readlines()]

            # Authenticate user
            if [username, password] in users:
                request.session["username"] = username  # Store session
                return redirect("dashboard")  # Redirect to dashboard

            return HttpResponse("Invalid credentials", status=401)
        except FileNotFoundError:
            return HttpResponse("Error: users.txt file not found.", status=500)

    return render(request, "login.html")  # Render login form (login.html template)


def dashboard_view(request):
    
    if "username" not in request.session:
        return redirect("home")  # Redirect to login if not authenticated

    
    # Render the dashboard.html template
    try:
        if not request.GET.get("day") is None:
            request.session["day"] = Day.DAY_OF_WEEK_CHOICES[request.GET.get("day")]
        
        if "day" not in request.session:
            request.session["day"] = Day.DAY_OF_WEEK_CHOICES["m"]
        print(request.session["day"])
    except:
        request.session["day"] = Day.DAY_OF_WEEK_CHOICES["m"]        
        
    try:  
        section_list = Section.objects.filter(time_slot__days__day_of_week = request.session["day"]).order_by('time_slot__start_time')
    except Section.DoesNotExist:
        section_list = []
    
    return render(request, "dashboard.html", {
        "username": request.session["username"], 
        "day": request.session["day"], 
        "section_list": section_list
        })


def section_view(request):
    
    
    if "username" not in request.session:
        return redirect("home")  # Redirect to login if not authenticated

    
    for variable in ["subject", "course_number", "section"]:
        if request.GET.get(variable) is None:
            print(f'{variable} is not set')
            return redirect("dashboard")
        else:
            request.session[variable] = request.GET.get(variable)
    
    selected_course = Course.objects.get(subject = request.session["subject"], class_number = request.session["course_number"])
    selected_section = Section.objects.get(course = selected_course, section_number = request.session["section"])        
    other_sections = Section.objects.filter(
        time_slot__days__in=selected_section.time_slot.days.all(),  # overlap in at least one day
        time_slot__start_time__lt=selected_section.time_slot.end_time,
        time_slot__end_time__gt=selected_section.time_slot.start_time,
    ).exclude(
        course=selected_section.course  # different course
    ).exclude(
        pk=selected_section.pk  # ignore the section itself
    ).distinct(
    ).order_by('time_slot__start_time')
    
    return render(request, "section_details.html", {
        "username": request.session["username"], 
        "day": request.session["day"],
        "section": selected_section,
        "other_section_list": other_sections,
        "same_semester": selected_course.same_semester_courses.all()
        })


def run_script(request):
    script_name = request.GET.get("script")
    script_path = os.path.join(
        settings.BASE_DIR, f"{script_name}.py"
    )  # Locate scripts in the root directory

    if os.path.exists(script_path):
        result = subprocess.run(["python", script_path], capture_output=True, text=True)
        return JsonResponse({"output": result.stdout, "error": result.stderr})
    else:
        return JsonResponse({"error": "Invalid script name"}, status=400)


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
    subjects_of_interest = {"CIST", "CSCI"}
    non_cs_subjects_of_interest = {"ENGL", "MATH", "CMST"}
    english_courses_of_interest = {"1150", "1160"}
    math_courses_of_interest = {"1950", "2050"}
    cmst_courses_of_interest = {"1110", "2120"}
    non_cs_courses_of_interest = {
        "engl1150",
        "cmst1110",
        "cmst2120",
        "math1950",
        "engl1160",
        "math2050",
    }
    filtered_courses = {latest_block: {}}
    non_filtered_courses = {latest_block: {}}

    for subject, courses in data[latest_block].items():
        if subject in subjects_of_interest or subject in non_cs_subjects_of_interest:
            filtered_courses[latest_block][subject] = courses
        # elif subject == "ENGL":
        #     english_courses = {
        #         course for course in courses if course in english_courses_of_interest
        #     }
        #     filtered_courses[latest_block][subject] = english_courses
        # elif subject == "MATH":
        #     math_courses = {
        #         course for course in courses if course in math_courses_of_interest
        #     }
        #     filtered_courses[latest_block][subject] = math_courses
        # elif subject == "CMST":
        #     cmst_courses = {
        #         course for course in courses if course in cmst_courses_of_interest
        #     }
        #     filtered_courses[latest_block][subject] = cmst_courses
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
    
    # Save model
    record = FilteredUpload.objects.create(
        filename=f"raw_input{upload_number}.json",
        filtered_data=filtered_courses,
        non_filtered_data=non_filtered_courses,
        uploaded_file=uploaded_file,
    )
    store_schedule(default_storage.path(filtered_filename))
    # === Convert filtered to ASP facts ===
    def convert24(time):
        t = datetime.strptime(time, "%I:%M%p")
        return t.hour * 60 + t.minute

    facts = []
    non_cs_classes, classes, rooms, professors, non_cs_times, times = (
        set(),
        set(),
        set(),
        set(),
        set(),
        set(),
    )

    for term, subjects in filtered_courses.items():
        for subject, courses in subjects.items():
            for course_num, course_info in courses.items():
                course_id = (
                    f"{subject}{course_num}".lower()
                    .replace(" ", "_")
                    .replace(".", "")
                    .replace("-", "_")
                )
                if (
                    subject in non_cs_subjects_of_interest
                    and course_id not in non_cs_courses_of_interest
                ):
                    continue
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
                    .replace("-", "_")
                    .replace(".", "")
                )

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
                    if subject in subjects_of_interest:
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
                    # Add critical sections for both CS and non-CS courses
                    if section_count == 1:
                        facts.append(f"critical_section({course_id}, {class_number}).")

                # ignore courses that are entirely comprised of totally online sections
                if totally_online_count == section_count:
                    continue

                # if we are a class that we can modify
                if subject in subjects_of_interest:
                    facts.append(f'course({course_id}, "{title}", "{prereq}").')
                    weight = 1
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
                    facts.append(f"course_weight({course_id}, {weight}, {year}).")
                    classes.add(course_id)
                # else we are a class like english or math and we cannot modify the time
                else:
                    facts.append(f'non_cs_course({course_id}, "{title}", "{prereq}").')
                    weight = 1
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
                    facts.append(f"course_weight({course_id}, {weight}, {year}).")
                    non_cs_classes.add(course_id)

    facts.append(f"class({'; '.join(classes)}).")
    facts.append(f"non_cs_class({'; '.join(non_cs_classes)}).")
    facts.append(f"room({'; '.join(rooms)}).")
    facts.append(f"professor({'; '.join(professors)}).")
    facts.extend(times)
    facts.extend(non_cs_times)

    asp_filename = raw_filename.replace(".json", ".lp")
    asp_filename = filtered_filename.replace(".json", ".lp")
    facts = convert(default_storage.path(filtered_filename))

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


from django.http import JsonResponse
import os
import clingo
from .models import FilteredUpload
from django.core.files.storage import default_storage


def run_clingo_solver(request):
    try:
        asp_filename = request.session.get("asp_filename")
        if not default_storage.exists(asp_filename):
            return JsonResponse(
                {"error": f"ASP file '{asp_filename}' not found."}, status=404
            )

        current_directory = os.path.dirname(os.path.realpath(__file__))
        path = current_directory.split(os.sep)
        root_index = path.index("Capstone-Team14")
        root_dir = os.sep.join(path[: root_index + 1])
        asp_file_path = os.path.join(root_dir, "media", asp_filename)
        clingo_dir = os.path.join(root_dir, "clingo")
        overlap_path = os.path.join(clingo_dir, "overlap_identifier.lp")

        ctl = clingo.Control()
        ctl.load(asp_file_path)
        ctl.load(overlap_path)
        ctl.ground()

        result = []

        def on_model(model):
            # Only collect shown atoms
            atoms = [str(s) for s in model.symbols(shown=True)]
            result.extend(atoms)

        ctl.solve(on_model=on_model)

        return JsonResponse(
            {
                "status": "success",
                "message": f"Clingo solver executed on {asp_filename}.",
                "models": result or ["No solution found."],
            }
        )

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


from django.http import JsonResponse, FileResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
import clingo
import re
import json
import os
from .models import FilteredUpload


@csrf_exempt
def optimize_schedule(request):
    try:
        asp_filename = request.session.get("asp_filename")
        if not asp_filename or not default_storage.exists(asp_filename):
            return JsonResponse({"error": "ASP file not found in session"}, status=404)

        # Define paths
        current_directory = os.path.dirname(os.path.realpath(__file__))
        path = current_directory.split(os.sep)
        root_index = path.index("Capstone-Team14")
        root_dir = os.sep.join(path[: root_index + 1])
        asp_path = os.path.join(root_dir, "media", asp_filename)
        minimizer_path = os.path.join(root_dir, "clingo", "overlap_minimizer.lp")

        # Temporary file path (output.json)
        temp_output_path = os.path.join(root_dir, "media", "output.json")

        # == Clingo Application Definition ==
        class ClingoApp(clingo.application.Application):
            def main(self, ctl, files):
                ctl.load(asp_path)
                ctl.load(minimizer_path)
                ctl.ground()
                ctl.solve()

            def print_model(self, model, printer):
                symbols = [str(s) for s in model.symbols(shown=True)]
                convert_to_json(symbols, temp_output_path)

        # == Supporting JSON Conversion Functions ==
        def convert_time(t):
            t = int(t)
            hours = t // 60
            minutes = t % 60
            suffix = "AM" if hours < 12 else "PM"
            hours = hours if hours <= 12 else hours - 12
            return f"{hours}:{minutes:02d}{suffix}"

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

        # == Run Clingo App ==
        clingo.application.clingo_main(ClingoApp())

        # == Save File via Django ==
        with open(temp_output_path, "r") as f:
            optimized_data = json.load(f)

        upload_count = FilteredUpload.objects.count() + 1
        optimized_filename = f"uploads/optimized_output{upload_count}.json"
        saved_path = default_storage.save(
            optimized_filename, ContentFile(json.dumps(optimized_data, indent=2))
        )

        # Optionally attach to latest upload
        try:
            latest_record = FilteredUpload.objects.latest("uploaded_at")
            latest_record.optimized_file.save(
                os.path.basename(saved_path),
                ContentFile(json.dumps(optimized_data, indent=2)),
            )
        except FilteredUpload.DoesNotExist:
            pass  # If no uploads yet, silently continue

        return JsonResponse(
            {
                "status": "success",
                "message": "Optimization complete.",
                "optimized_file": saved_path,
                "optimized_data": optimized_data,
            }
        )

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def download_optimized_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, "uploads", filename)
    if os.path.exists(file_path):
        return FileResponse(
            open(file_path, "rb"), as_attachment=True, filename=filename
        )
    return JsonResponse({"error": "File not found"}, status=404)

def run_clingo_optimizer(request):
    try:
        asp_filename = request.session.get("asp_filename")
        if not default_storage.exists(asp_filename):
            return JsonResponse({"error": f"ASP file '{asp_filename}' not found."}, status=404)

        current_directory = os.path.dirname(os.path.realpath(__file__))
        path = current_directory.split(os.sep)
        root_index = path.index("Capstone-Team14")
        root_dir = os.sep.join(path[: root_index + 1])
        asp_file_path = os.path.join(root_dir, "media", asp_filename)
        clingo_dir = os.path.join(root_dir, "clingo")
        overlap_path = os.path.join(clingo_dir, "overlap_minimizer.lp")

        ctl = clingo.Control()
        # ctl.load(asp_file_path)
        ctl.load(overlap_path)
        ctl.ground()

        result = []

        def on_model(model):
            # Only collect shown atoms
            symbols = [str(s) for s in list(model.symbols(shown=True))]
            # print(symbols)

            convert_to_json(symbols, "media\output.json")

        ctl.solve(on_model=on_model)

        return JsonResponse({
            "status": "success",
            "message": f"Clingo solver executed on {asp_filename}.",
            "models": result or ["No solution found."]
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

def run_clingo_optimizer(request):
    try:
        asp_filename = request.session.get("asp_filename")
        if not default_storage.exists(asp_filename):
            return JsonResponse({"error": f"ASP file '{asp_filename}' not found."}, status=404)

        current_directory = os.path.dirname(os.path.realpath(__file__))
        path = current_directory.split(os.sep)
        root_index = path.index("Capstone-Team14")
        root_dir = os.sep.join(path[: root_index + 1])
        asp_file_path = os.path.join(root_dir, "media", asp_filename)
        clingo_dir = os.path.join(root_dir, "clingo")
        overlap_path = os.path.join(clingo_dir, "overlap_minimizer.lp")

        ctl = clingo.Control()
        # ctl.load(asp_file_path)
        ctl.load(overlap_path)
        ctl.ground()

        result = []

        def on_model(model):
            # Only collect shown atoms
            symbols = [str(s) for s in list(model.symbols(shown=True))]
            # print(symbols)

            convert_to_json(symbols, "media\output.json")

        ctl.solve(on_model=on_model)

        return JsonResponse({
            "status": "success",
            "message": f"Clingo solver executed on {asp_filename}.",
            "models": result or ["No solution found."]
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
        
        
"""
# Ideal method for converting to clingo

def run_solver(request):
    # ==== Convert DB to Rules ====
    # ========  Get Objects
    objects = Room.objects.all()
    objects.extend(Day.objects.all())
    objects.extend(Course.objects.all())
    objects.extend(Requirement.objects.all())
    objects.extend(Section.objects.all())
    objects.extend(PlanSemester.objects.all())
    with open(filename, w) as f:
        for object in objects:
            f.write(object.print_clingo())
            f.write('\n')

"""