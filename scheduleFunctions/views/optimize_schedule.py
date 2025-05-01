from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
import json
import os
from ..models import FilteredUpload
from .clingo_helpers import (
    run_clingo_optimization,
    get_root_path,
    convert_to_json,
    load_optimized_json,
    save_optimized_file,
)


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
