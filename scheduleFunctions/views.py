import subprocess
from django.http import JsonResponse
from django.shortcuts import render

def home(request):
    return render(request, "index.html")  # Renders the template

import os
import subprocess
from django.http import JsonResponse
from django.conf import settings

def run_script(request):
    script_name = request.GET.get("script")
    script_path = os.path.join(settings.BASE_DIR, f"{script_name}.py")  # Locate scripts in the root directory

    if os.path.exists(script_path):
        result = subprocess.run(["python", script_path], capture_output=True, text=True)
        return JsonResponse({"output": result.stdout, "error": result.stderr})
    else:
        return JsonResponse({"error": "Invalid script name"}, status=400)

