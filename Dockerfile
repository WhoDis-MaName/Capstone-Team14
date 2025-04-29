# Use the official Python runtime image
FROM python:3.13-slim  
 
# Create the app directory
RUN mkdir /Capstone-Team14
 
# Set the working directory inside the container
WORKDIR /Capstone-Team14
 
# Set environment variables 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 
 
# Upgrade pip
RUN pip install --upgrade pip 
 
# Copy the Django project  and install dependencies
COPY requirements.txt  /Capstone-Team14/
 
# run this command to install all dependencies 
RUN pip install --no-cache-dir -r requirements.txt

# Build Database and load default days into it
RUN python manage.py makemigrations
RUN python manage.py migrate
RUN python manage.py loaddata scheduleFunctions/fixtures/prepopulated.json
 
# Copy the Django project to the container
COPY . /Capstone-Team14/
 
# Expose the Django port
EXPOSE 8000
 
# Run Django’s development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]