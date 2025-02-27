import subprocess
from django.http import JsonResponse
from django.shortcuts import render

def home(request):
    return render(request, "index.html")  # Renders the template

def run_script(request):
    script_name = request.GET.get("script")  # Get user input from URL parameter

    if script_name == "converter":
        result = subprocess.run(["python", "converter.py"], capture_output=True, text=True)
    elif script_name == "processor":
        result = subprocess.run(["python", "processor.py"], capture_output=True, text=True)
    elif script_name == "demo":
        result = subprocess.run(["python", "demo.lp"], capture_output=True, text=True)
    else:
        return JsonResponse({"error": "Invalid script name"}, status=400)

    return JsonResponse({"output": result.stdout, "error": result.stderr})
