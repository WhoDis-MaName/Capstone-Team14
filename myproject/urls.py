"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from scheduleFunctions.views import run_script  # Import the view for schedulerApp functions
from scheduleFunctions.views import login, dashboard_view, upload_json_file, run_clingo_solver, download_optimized_file, optimize_schedule, run_clingo_optimizer, section_view
urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('run-script/', run_script, name='run_script'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('section/', section_view, name='section'),
    path('', login, name='home'),  # Add homepage route
    path('upload/', upload_json_file, name='upload_json_file'),
    path("run-solver/", run_clingo_solver, name="run_clingo_solver"),
    path("optimize-schedule/", optimize_schedule, name="optimize_schedule"),
    path("download/<str:filename>/", download_optimized_file, name="download_file"),
    path("optimize/", run_clingo_optimizer, name="run_clingo_optimizer"),
]
