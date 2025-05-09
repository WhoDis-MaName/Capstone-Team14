from django.shortcuts import render, redirect
from scheduleFunctions.models import Course, Section, Proffessor
from django.http import JsonResponse

##
# @brief Displays a page where professors are able to set their own preferences on when they teach classes.
#
# This view retrieves the session data for the authenticated user and either generates the 'professor_preference.html' template with all the available professors,
# or retrieves data from the form and then updates the preferences that are stored in the database.
#
# @param request The HTTP request object containing the session data or POST parameters providing the preferences.
# @return A rendered HTML response with the 'professor_preference.html' template, including the selected section details, 
#         a list of overlapping sections, and courses from the same semester, or a redirect to the dashboard or login page if data is missing.
def preferences_view(request):
    if "username" not in request.session:
        return redirect("home")  # Redirect to login if not authenticated
    
    if request.method != "POST":
        return render(
            request,
            "professor_preference.html",
            {
                "username": request.session["username"],
                "day": request.session["day"],
                "professors": Proffessor.objects.all(),
            },
        )
        ...
        
    else:
        professors = Proffessor.objects.all()
        
        try:
            for professor in professors:
                selected_days = request.POST.getlist(f'{professor.pk}-day-preference')
                professor.day_preferences.set(selected_days)
                professor.time_preferences = request.POST.getlist(f'{professor.pk}-time-preference')
            return JsonResponse(
                {
                    "message": f"Modifications complete."
                }
            )
        except Exception as e:
            print(e)
            return JsonResponse(
                {
                    "error": f"Something went wrong."
                }
            )
        ...