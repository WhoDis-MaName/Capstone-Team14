from django.contrib import admin
from .models import FilteredUpload

@admin.register(FilteredUpload)
class FilteredUploadAdmin(admin.ModelAdmin):
    list_display = ('filename', 'uploaded_at')
    ordering = ('-uploaded_at',)
