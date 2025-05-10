from django.shortcuts import render, redirect
from scheduleFunctions.models import Section, Day
from scheduleFunctions.to_database import clear_schedule

##
# @brief Displays the dashboard page for the authenticated user.
#
# This view retrieves the session data for the authenticated user, validates and sets the current day based on the 
# GET request, or defaults to Monday if no valid day is provided. It then attempts to fetch a list of sections 
# for the selected day from the database and orders them by start time. If no sections are found for the selected day, 
# it returns an empty list. The view then renders the 'dashboard.html' template with the username, selected day, 
# and the list of sections for that day.
#
# @param request The HTTP request object containing the session data and GET parameters for the day.
# @return A rendered HTML response with the 'dashboard.html' template, including the username, selected day, 
#         and the list of sections for the selected day, or a redirect to the login page if the user is not authenticated.
def dashboard_view(request):

    if "username" not in request.session:
        return redirect("home")  # Redirect to login if not authenticated

    # Render the dashboard.html template
    
        
    try:
        if not request.GET.get("day") is None:
            request.session["day"] = Day.DAY_OF_WEEK_CHOICES[request.GET.get("day")]

        if "day" not in request.session:
            request.session["day"] = Day.DAY_OF_WEEK_CHOICES["m"]
        print(request.session["day"])
    except:
        request.session["day"] = Day.DAY_OF_WEEK_CHOICES["m"]
        
    try:
        if not request.GET.get("changed") is None:
            request.session["changed"] = True
            request.session["day"] = "Changed Sessions"
        else:
            request.session["changed"] = False
            if request.session["day"] == "Changed Sessions":
                request.session["day"] = Day.DAY_OF_WEEK_CHOICES["m"]
    except:
        request.session["changed"] = False

    try:
        if request.session["changed"]:
            section_list = Section.objects.filter(
                # time_slot__days__day_of_week=request.session["day"],
                changed = True
            ).order_by("time_slot__start_time")
            # print(section_list)
        else:
            section_list = Section.objects.filter(
                time_slot__days__day_of_week=request.session["day"]
            ).order_by("time_slot__start_time")
    except Section.DoesNotExist:
        section_list = []

    return render(
        request,
        "dashboard.html",
        {
            "username": request.session["username"],
            "day": request.session["day"],
            "section_list": section_list,
        },
    )