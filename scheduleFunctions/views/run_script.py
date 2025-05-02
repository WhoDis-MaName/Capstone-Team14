from django.http import JsonResponse
import os
from django.conf import settings
import subprocess

# TODO: What does this do? Is this used for anything? 
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
