import os
import subprocess
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from .models import FilteredUpload
import json
from django.http import JsonResponse
from django.core.files.base import ContentFile  # <-- Add this line
from .models import FilteredUpload
from django.core.files.storage import default_storage
from django.utils.timezone import now
from django.core.files.base import ContentFile


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
    return render(request, "dashboard.html", {"username": request.session["username"]})

def run_script(request):
    script_name = request.GET.get("script")
    script_path = os.path.join(settings.BASE_DIR, f"{script_name}.py")  # Locate scripts in the root directory

    if os.path.exists(script_path):
        result = subprocess.run(["python", script_path], capture_output=True, text=True)
        return JsonResponse({"output": result.stdout, "error": result.stderr})
    else:
        return JsonResponse({"error": "Invalid script name"}, status=400)

@csrf_exempt  
def upload_json_file(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return JsonResponse({"error": "No file provided"}, status=400)

    if not uploaded_file.name.lower().endswith('.json'):
        return JsonResponse({"error": "Only .json files are allowed"}, status=400)

    try:
        # Copy uploaded file's contents and reset pointer after read
        file_contents = uploaded_file.read()
        data = json.loads(file_contents)
        uploaded_file.seek(0)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Uploaded file is not a valid JSON file"}, status=400)

    if not data:
        return JsonResponse({"error": "The JSON file is empty"}, status=400)

    latest_block = max(data.keys())
    subjects_of_interest = {"CIST", "CSCI"}
    filtered_courses = {latest_block: {}}
    non_filtered_courses = {latest_block: {}}

    latest_subjects = data[latest_block]
    for subject_code, courses_dict in latest_subjects.items():
        if subject_code in subjects_of_interest:
            filtered_courses[latest_block][subject_code] = courses_dict
        else:
            non_filtered_courses[latest_block][subject_code] = courses_dict

    # === NEW NAMING LOGIC ===
    upload_number = FilteredUpload.objects.count() + 1

    raw_filename = f"uploads/raw_input{upload_number}.json"
    filtered_filename = f"uploads/filtered_output{upload_number}.json"
    non_filtered_filename = f"uploads/remaining_output{upload_number}.json"

    # Save files to media/uploads/
    default_storage.save(raw_filename, ContentFile(file_contents))
    default_storage.save(filtered_filename, ContentFile(json.dumps(filtered_courses, indent=2)))
    default_storage.save(non_filtered_filename, ContentFile(json.dumps(non_filtered_courses, indent=2)))

    # Save to DB
    FilteredUpload.objects.create(
        filename=f"raw_input{upload_number}.json",
        filtered_data=filtered_courses,
        non_filtered_data=non_filtered_courses,
        uploaded_file=uploaded_file  # Will use original name
    )

    return JsonResponse({
        "message": f"Upload #{upload_number} complete.",
        "raw_file": raw_filename,
        "filtered_file": filtered_filename,
        "non_filtered_file": non_filtered_filename,
        "filtered_courses": filtered_courses,
        "non_filtered_courses": non_filtered_courses
    }, safe=False)


def convert24(time):
    t = datetime.strptime(time, "%I:%M%p")
    return t.hour * 60 + t.minute
# mayve tghsiu will help or something
def run_converter(request):
    try:
        latest = FilteredUpload.objects.latest("uploaded_at")
        file_path = latest.uploaded_file.path

        with open(file_path, "r") as f:
            data = json.load(f)

        facts = []
        classes, rooms, professors, times = set(), set(), set(), set()

        for term, subjects in data.items():
            for subject, courses in subjects.items():
                for course_num, course_info in courses.items():
                    course_id = f"{subject}{course_num}".lower().replace(" ", "_").replace(".", "").replace("-", "_")
                    title = course_info.get("title", "").lower().replace(" ", "_").replace(".", "").replace("-", "_")
                    prereq = course_info.get("prereq", "none").lower().replace(" ", "_").replace("-", "_").replace(".", "")

                    facts.append(f'course({course_id}, "{title}", {prereq}).')
                    classes.add(course_id)

                    for section_num, section_info in course_info.get("sections", {}).items():
                        section_num = "s" + section_num.lower()
                        class_number = "c" + section_info.get("Class Number", "").split()[0].lower()

                        time = section_info.get("Time", "TBA")
                        if time == "TBA":
                            start, end = "tba", "tba"
                        else:
                            start, end = time.split(" - ")
                            start = convert24(start)
                            end = convert24(end)

                        days = section_info.get("Days", "TBA").strip().lower().replace(" ", "_").replace("-", "_")
                        location = section_info.get("Location", "Unknown").lower().replace(" ", "_").replace(".", "").replace("-", "_")
                        instructor = section_info.get("Instructor", "Unknown").lower().replace(" ", "_").replace(".", "").replace("-", "_")

                        if location in {"totally_online", "to_be_announced"} or start == "tba":
                            continue

                        facts.append(f"section({course_id}, {section_num}, {class_number}, {start}, {end}, {days}, {location}, {instructor}).")
                        rooms.add(location)
                        professors.add(instructor)
                        if start != "tba" and end != "tba" and days != "tba":
                            times.add(f"time_slot({start}, {end}, {days}).")

        facts.append(f"class({'; '.join(classes)}).")
        facts.append(f"room({'; '.join(rooms)}).")
        facts.append(f"professor({'; '.join(professors)}).")
        facts.extend(times)

        # Write the .lp file
        asp_filename = file_path.replace(".json", ".lp")
        with open(asp_filename, "w") as out_file:
            out_file.write("\n".join(facts))

        return JsonResponse({"success": True, "message": f"Conversion completed! ASP facts saved to {asp_filename}"})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
