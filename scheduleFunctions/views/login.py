from django.shortcuts import render, redirect
import os
from django.http import HttpResponse

##
# @brief Displays the dashboard page for the authenticated user.
#
# This view retrieves the user's session data and, if authenticated, renders the dashboard page. 
# It handles the selection of a day of the week (from the "day" parameter in the GET request) 
# and filters sections based on the selected day. If no valid day is provided, it defaults to Monday.
# It also handles errors gracefully if the section data cannot be retrieved.
#
# @param request The HTTP request object containing the session data, including the 'day' and 'username'.
# @return A rendered HTML response with the 'dashboard.html' template, including a list of sections for
#         the selected day and the username, or a redirect to the login page if the user is not authenticated.
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Get the absolute path to users.txt
        current_dir = os.path.dirname(os.path.abspath(__file__))
        users_file_path = os.path.join(current_dir, "..","users.txt")

        try:
            # Read users.txt
            with open(users_file_path, "r") as file:
                users = [line.strip().split(",") for line in file.readlines()]

            # Authenticate user
            if [username, password] in users:
                request.session["username"] = username  # Store session
                return redirect("dashboard")  # Redirect to dashboard

            return HttpResponse("Invalid credentials", status=401)
        except FileNotFoundError:
            return HttpResponse("Error: users.txt file not found.", status=500)

    return render(request, "login.html")  # Render login form (login.html template)
