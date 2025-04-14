from datetime import datetime
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

    # === Convert filtered to ASP facts ===
    def convert24(time):
        t = datetime.strptime(time, "%I:%M%p")
        return t.hour * 60 + t.minute

    facts = []
    classes, rooms, professors, times = set(), set(), set(), set()

    for term, subjects in filtered_courses.items():
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
                    .replace("-", "_")
                    .replace(".", "")
                )

                facts.append(f'course({course_id}, "{title}", "{prereq}").')
                classes.add(course_id)

                for section_num, section_info in course_info.get("sections", {}).items():
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

                    days = section_info.get("Days", "TBA").strip().lower().replace(" ", "_").replace("-", "_")
                    location = section_info.get("Location", "Unknown").lower().replace(" ", "_").replace(".", "").replace("-", "_")
                    instructor = section_info.get("Instructor", "Unknown").lower().replace(" ", "_").replace(".", "").replace("-", "_")

                    if location in {"totally_online", "to_be_announced"} or start == "tba":
                        continue

                    facts.append(
                        f"section({course_id}, {section_num}, {class_number}, {start}, {end}, {days}, {location}, {instructor})."
                    )
                    rooms.add(location)
                    professors.add(instructor)
                    if start != "tba" and end != "tba" and days != "tba":
                        times.add(f"time_slot({start}, {end}, {days}).")

    facts.append(f"class({'; '.join(classes)}).")
    facts.append(f"room({'; '.join(rooms)}).")
    facts.append(f"professor({'; '.join(professors)}).")
    facts.extend(times)

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
