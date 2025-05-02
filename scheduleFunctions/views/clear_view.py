from django.shortcuts import render, redirect
from scheduleFunctions.models import Section, Day
from scheduleFunctions.to_database import clear_schedule

def clear_view(request):
    if "username" not in request.session:
        return redirect("home")  # Redirect to login if not authenticated
    
    clear_schedule()
    return redirect("dashboard")