from django.db import models

class FilteredUpload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255)  # This will store the original uploaded filename
    filtered_data = models.JSONField()
    non_filtered_data = models.JSONField()
    uploaded_file = models.FileField(upload_to='uploads/')  # Raw input file

    # Optional: Add these new fields to store the saved file paths
    raw_file_path = models.CharField(max_length=255, blank=True)
    filtered_file_path = models.CharField(max_length=255, blank=True)
    remaining_file_path = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.filename} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"
