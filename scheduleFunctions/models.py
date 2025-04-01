from django.db import models

class FilteredUpload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255)
    filtered_data = models.JSONField()
    uploaded_file = models.FileField(upload_to='uploads/')

    def __str__(self):
        return f"{self.filename} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"
