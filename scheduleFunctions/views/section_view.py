from django.shortcuts import render, redirect
from scheduleFunctions.models import Course, Section
from django.http import JsonResponse

##
# @brief Displays details of a specific course section.
#
# This view retrieves the session data for the authenticated user and validates that the required parameters 
# ("subject", "course_number", and "section") are provided in the GET request. If any parameter is missing, 
# it redirects the user back to the dashboard. It fetches the selected course and section from the database 
# and also retrieves any other sections that overlap in time with the selected section. The view then renders 
# the 'section_details.html' template with the details of the selected section and a list of overlapping sections.
#
# @param request The HTTP request object containing the session data and GET parameters for subject, course number, and section.
# @return A rendered HTML response with the 'section_details.html' template, including the selected section details, 
#         a list of overlapping sections, and courses from the same semester, or a redirect to the dashboard or login page if data is missing.
def section_view(request):
    if "username" not in request.session:
        return redirect("home")  # Redirect to login if not authenticated
    
    if request.method == "POST":
        selected_course = Course.objects.get(
            subject=request.session["subject"],
            class_number=request.session["course_number"],
        )
        other_sections = (
            Section.objects.filter(
                time_slot__days__in=selected_section.time_slot.days.all(),  # overlap in at least one day
                time_slot__start_time__lt=selected_section.time_slot.end_time,
                time_slot__end_time__gt=selected_section.time_slot.start_time,
            )
            .exclude(course=selected_course)  # different course
            .distinct()
            #.exclude(section_id=selected_section.section_id)  # ignore the section itself
            .order_by("time_slot__start_time")
        )
        try:
            for other_section in other_sections:
                variable = other_section.pk
                if not request.POST.get(variable) is None:
                    if request.POST.get(variable) == "True":
                        selected_course.same_semester_courses.add(other_section.course)
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
                  
            

    if "username" not in request.session:
        return redirect("home")  # Redirect to login if not authenticated

    for variable in ["subject", "course_number", "section"]:
        if request.GET.get(variable) is None:
            print(f"{variable} is not set")
            return redirect("dashboard")
        else:
            request.session[variable] = request.GET.get(variable)

    selected_course = Course.objects.get(
        subject=request.session["subject"],
        class_number=request.session["course_number"],
    )
    selected_section = Section.objects.get(
        course=selected_course, section_number=request.session["section"]
    )
    other_sections = (
        Section.objects.filter(
            time_slot__days__in=selected_section.time_slot.days.all(),  # overlap in at least one day
            time_slot__start_time__lt=selected_section.time_slot.end_time,
            time_slot__end_time__gt=selected_section.time_slot.start_time,
        )
        .exclude(course=selected_course)  # different course
        .distinct()
        #.exclude(section_id=selected_section.section_id)  # ignore the section itself
        .order_by("time_slot__start_time")
    )
    for section in other_sections:
        print(section.print_clingo())

    return render(
        request,
        "section_details.html",
        {
            "username": request.session["username"],
            "day": request.session["day"],
            "section": selected_section,
            "other_section_list": other_sections,
            "same_semester": selected_course.same_semester_courses.all(),
        },
    )
