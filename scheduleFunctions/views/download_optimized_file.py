from django.conf import settings
import os
from django.http import JsonResponse, FileResponse


def download_optimized_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, "uploads", filename)
    if os.path.exists(file_path):
        return FileResponse(
            open(file_path, "rb"), as_attachment=True, filename=filename
        )
    return JsonResponse({"error": "File not found"}, status=404)
