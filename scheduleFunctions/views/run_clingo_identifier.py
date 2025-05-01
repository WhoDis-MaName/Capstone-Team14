from django.http import JsonResponse
import os
import clingo
from ..models import FilteredUpload
from django.core.files.storage import default_storage
from .clingo_helpers import *


def run_clingo_identifier(request):
    try:
        asp_filename = request.session.get("asp_filename")
        if not default_storage.exists(asp_filename):
            return JsonResponse(
                {"error": f"ASP file '{asp_filename}' not found."}, status=404
            )

        last_model_symbols = run_clingo_optimization(
            asp_filename, "overlap_identifier.lp"
        )

        return JsonResponse(
            {
                "status": "success",
                "message": f"Clingo solver executed on {asp_filename} with result = {last_model_symbols}",
                "models": last_model_symbols,
            }
        )

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
