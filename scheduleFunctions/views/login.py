from django.shortcuts import render, redirect
import os
from django.http import HttpResponse


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Get the absolute path to users.txt
        current_dir = os.path.dirname(os.path.abspath(__file__))
        users_file_path = os.path.join(current_dir, "..\\users.txt")

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
