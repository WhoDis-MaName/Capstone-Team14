import os
import subprocess
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings


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

"""
<li>CSCI 1620 - Introduction to CS (Mon/Wed 10:00AM - 11:30AM)</li>
<li>MATH 1950 - Calculus I (Tue/Thu 1:00PM - 2:30PM)</li>
<li>MATH 2040 - Discrete Math (Mon/Wed 3:00PM - 4:15PM)</li>
<li>GEOG 1010 - Geology (Mon/Wed 3:00PM - 4:15PM)</li>
"""
example_course_list = [
    {
        'course_number': "CSCI 1620",
        'id': 1,
        'name': 'Introduction to CS',
        'days': ['Mon','Wed'],
        'start': '10:00AM',
        'end': '11:30AM'
    },
    {
        'course_number': "MATH 1950",
        'id': 1,
        'name': 'Calculus I',
        'days': ['Tue','Thu'],
        'start': '1:00PM',
        'end': '2:30PM'
    },
    {
        'course_number': "MATH 2040",
        'id': 1,
        'name': 'Discrete Math',
        'days': ['Mon','Wed'],
        'start': '3:00PM',
        'end': '4:15PM'
    },
    {
        'course_number': "GEOG 1010",
        'id': 1,
        'name': 'Geology',
        'days': ['Mon','Wed'],
        'start': '3:00PM',
        'end': '4:15PM'
    }
]

example_conflict_list = [
    ["MATH 2040", "GEOG 101"],
]

def schedule_view(request):
    # if "username" not in request.session:
    #     return redirect("home")  # Redirect to login if not authenticated

    selected_course = request.GET.get('course', None) 
    selected_section =request.GET.get('section', None) 
    if selected_course and selected_section:
        return render(request, "section_details.html", {"username": request.session["username"], "details": get_section_details(selected_course, selected_section)})
    # Render the dashboard.html template
    return render(request, "schedule.html", {"username": request.session["username"], "course_list": example_course_list, "conflict_list": example_conflict_list})

def run_script(request):
    script_name = request.GET.get("script")
    script_path = os.path.join(settings.BASE_DIR, f"{script_name}.py")  # Locate scripts in the root directory

    if os.path.exists(script_path):
        result = subprocess.run(["python", script_path], capture_output=True, text=True)
        return JsonResponse({"output": result.stdout, "error": result.stderr})
    else:
        return JsonResponse({"error": "Invalid script name"}, status=400)


def get_section_details(course: str, section: int) -> dict:
    """Returns a dictionary detailing all the relevant information for the section that is requested.

    Args:
        course (str): identifier for the course that the section is part of. i.e. csci2500
        section (int): number for the section

    Returns:
        dict: All of the information relevant to the section.
            'course': str
            'section': int
            'start': int
            'end': int
            'days': list[str]
            'course_name': str
            'desc': str
            'professor': str
            'location': str
            'prerequisites': list[str]
            'cocurrent_classes': list[dict]
                'course': str
                'section': str
                'course_name': str
                'start': int
                'end': int
                'days': list[str]
            
    """
    ...