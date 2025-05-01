from django.shortcuts import render, redirect
from scheduleFunctions.models import Section, Day


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
