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
        
    day_object = Day.objects.get(day_of_week = request.session["day"])

    try:  
        section_list = Section.objects.filter(days = day_object).order_by('start_time')
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
        days__in=selected_section.days.all(),  # overlap in at least one day
        start_time__lt=selected_section.end_time,
        end_time__gt=selected_section.start_time,
    ).exclude(
        course=selected_section.course  # different course
    ).exclude(
        pk=selected_section.pk  # ignore the section itself
    ).distinct(
    ).order_by('start_time')
    
    print(selected_course.same_semester_courses.all())
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
    filtered_courses = {latest_block: {}}
    non_filtered_courses = {latest_block: {}}

    for subject, courses in data[latest_block].items():
        if subject in subjects_of_interest:
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
    
    # Save model
    record = FilteredUpload.objects.create(
        filename=f"raw_input{upload_number}.json",
        filtered_data=filtered_courses,
        non_filtered_data=non_filtered_courses,
        uploaded_file=uploaded_file,
    )
    store_schedule(default_storage.path(filtered_filename))
    # === Convert filtered to ASP facts ===
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
            return JsonResponse({"error": f"ASP file '{asp_filename}' not found."}, status=404)

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