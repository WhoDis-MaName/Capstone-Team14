from django.conf import settings
import os
from django.http import JsonResponse, FileResponse

##
# @brief Handles the download of an optimized file.
#
# This view attempts to locate and return the requested file for download. If the file exists
# in the specified directory, it is served as an attachment. If the file does not exist, a 404 
# error response is returned.
#
# @param request The HTTP request object, which includes the 'filename' parameter as part of the URL.
# @param filename The name of the file to be downloaded. This should correspond to a file located in
#        the 'uploads' directory under MEDIA_ROOT.
# @return A FileResponse to serve the file as an attachment if it exists, or a JsonResponse with
#         an error message and a 404 status if the file is not found.
def download_optimized_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, "uploads", filename)
    if os.path.exists(file_path):
        return FileResponse(
            open(file_path, "rb"), as_attachment=True, filename=filename
        )
    return JsonResponse({"error": "File not found"}, status=404)
