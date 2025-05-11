from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
import json
import os
from scheduleFunctions.models import FilteredUpload, Section
from .clingo_helpers import (
    run_clingo_optimization,
    get_root_path,
    convert_to_json,
    load_optimized_json,
    save_optimized_file,
)


##
# Run the clingo program for proposing an optimal schedule. 
#
# Like with the conflict identifier, we randomly choose one section from each course to be called "critical".
#
# For each course in the input file, we suggest a new timeslot. A timeslot if an object encoding the 
# start time, end time, and day of a particular section. These timeslots are restricted to credit hours. 
# For example, some timeslots are only for 1 credit hour courses, while others are for 3 credit hour courses. 
#
# We then ensure that no two sections are in the same room at the same time, 
# and no professors are scheduled for two or more sections at the same time. 
#
# We then define conflict such that two sections have overlapping times, overlapping days, and are not sections of the same class. 
# 
# We then define a critical conflict to be if two critical sections of the same year (ie, two 3000 level courses) are in conflict. 
# 
# We then minimize the count of critical conflicts. 
# As a secondary objective, we additionally minimize the number of changes from the original schedule.
# 
# In progress: Working on implementing professor preferences as tertiary objectives such as:
# - Morning times
# - Afternoon times
# - Back to back times
# - Monday/Wednesday Dayslots
# - Tuesday/Thursday Dayslots
@csrf_exempt
def optimize_schedule(request):
    try:
        root_dir = get_root_path()
        asp_filename = request.session.get("asp_filename")
        temp_output_path = os.path.join(root_dir, "media", "output.json")

        if not asp_filename or not default_storage.exists(asp_filename):
            return JsonResponse({"error": "ASP file not found in session"}, status=404)

        last_model_symbols = run_clingo_optimization(
            asp_filename, "overlap_minimizer.lp"
        )

        # Convert and write the output to JSON
        convert_to_json(last_model_symbols, temp_output_path)

        optimized_data = load_optimized_json(temp_output_path)

        # Save file to media
        upload_count = FilteredUpload.objects.count() + 1
        optimized_filename = f"uploads/optimized_output{upload_count}.json"
        saved_path = save_optimized_file(optimized_data, optimized_filename)

        # Attach to latest record if available
        try:
            latest_record = FilteredUpload.objects.latest("uploaded_at")
            latest_record.optimized_file.save(
                os.path.basename(saved_path),
                ContentFile(json.dumps(optimized_data, indent=2)),
            )
        except FilteredUpload.DoesNotExist:
            pass

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
