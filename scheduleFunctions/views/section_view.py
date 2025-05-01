from django.shortcuts import render, redirect
from scheduleFunctions.models import Course, Section


def section_view(request):

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
        .exclude(course=selected_section.course)  # different course
        .exclude(pk=selected_section.pk)  # ignore the section itself
        .distinct()
        .order_by("time_slot__start_time")
    )

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
