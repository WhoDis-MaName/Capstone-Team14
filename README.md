# Course Schedule Optimization

## Project Overview

This project aims to identify conflicting courses that students are likely to take simultaneously and propose a new schedule without conflicts. The main objectives include:

1. **Identifying Time Conflicts** between classes commonly taken in the same semester.
2. **Optimizing the Schedule** to minimize conflicts with minimal changes to the original schedule.
3. **Handle Professor Preferences** - Given a list of professor preferences, respect these preferences during the optimization step.

---

## Identifying Conflicts

Each course as a list of sections which encode the following information:

- Unique Section ID
- Section number (ie: 001)
- Section timeslot (Start time, End time, Days)
- Room
- Professor

There is a **scheduling conflict** between two sections if they:

- Have the overlapping times **and** overlapping days
- Are predicted to be taken during the same year
- Are **not** sections of the same course or cross listed together.

We randomly assign one section to be labeled the **critical section** for each course. There is a **critical conflict** between two courses if their **critical sections** are in conflict.

---

## Optimization Approach

After identifying the critical conflicts, the next step is to suggest a reorganized schedule. The optimization criteria include:

- **Minimizing the number of critcal conflicts.**
- **Minimize the number of preference violations.**
- **Minimize the number of changes to the original schedule.**

## A critical conflict count of zero means that it is possible to select at least one section from any course without conflicting times for courses of a particular year

## Future Improvements

- Gather feedback from faculty to refine scheduling priorities.
- Explore additional factors such as classroom constraints.
- Add professor preferences to the UI
- Transition to generating clingo facts from database instead of generating them on file upload
- Maintain a record of the old TimeSlots when Sections are changed
- Expand capabilites to other departments
  - Allow users to provide links to 4-year plans
  - Allow users to provide links to degree requirements
- Have user assignments by department and user type
- Differentiate experience between registrar user, advisor user, and professor user
  - Registrar user can upload, view, optimize, and download the schedule (including differences)
  - Advisor user can view uploaded schedule and provide feedback
  - Professor user can view uploaded schedule and update preferences

---

## Release Notes Version 0.1

### Command Line Deployment

To run the project, simply launch your virtual environment using:

`source myenv/bin/activate`

After entering virtual environment, download Django:

`pip install -r requirements.txt`

Also Following the steps to install Clingo:

<https://github.com/potassco/clingo?tab=readme-ov-file>

To Launch the current iteration of project, use these commands from inside the root directory for the project (Capstone-14):

`python manage.py runserver`

- This release has mainly included a foundation for each section(front-end, back-end, and ASP). We've created basic python scripts for parsing through the schedule JSON file and a simple pipeline to convert the filtered CSCI class into ASP formatted rules and constraints. From this, we're able to run a basic constraint identifier that returns which classes conflict with one another. Additionally, we were able to set up two basic buttons that execute this "Check Conflicts" and "Optimize Schedule".

To launch django tests, use this command:

`python manage.py test`

We also integrated pytest to test the clingo code. To use pytest, navigate to `\testing\clingo_tests` and use this command:

`pytest -v .\clingo_pytest.py`

### Docker Deployment

To build the docker containter image, move to the root directory for the repository and run:

`sudo docker build -t capstone-14:latest .`

Run the container using:

`sudo docker run --name capstone-14 -p 8000:8000 capstone-14`

_Note_ the docker deployment will not perform any tests.

### Some helpful notes on running clingo

can use `-t` to specify number of threads for clingo. Ie: `clingo overlap_minizer.lp -t 8`.

The following code shows how to run Clingo with a few different options. We have `--opt-mode=optN` which shows multiple optimal models. `10` means only show `10` optimal models. `-t 2` means use 2 threads:

`clingo --opt-mode=optN ../media/uploads/raw_input5.lp .\overlap_minimizer.lp 10 -t 2`

This can be called through python with the following:

`ctl = clingo.Control(["10", "--opt-mode=optN", "-t", "2"])`

## Branches for Version 0.1

- origin/josh/test: Josh and Andra worked on some pytest implementations
- orign/andra-test2: Test the django testing suite. Also tested a template Dockerfile
- orign/andra-test2: Test the django testing suite
- orign/main: Vlad and Francisco worked to implement front-end styling on the main branch

## Release Notes Version 0.2

To run the project, simply launch your virtual environment using:

`source myenv/bin/activate`

After entering virtual environment, download Django:

`pip install django`

Also Following the steps to install Clingo:

<https://github.com/potassco/clingo?tab=readme-ov-file>

To Launch the current iteration of project, use this command:

`python manage.py runserver`

- This release has mainly included a foundation for each section(front-end, back-end, and ASP). We've created basic python scripts for parsing through the schedule JSON file and a simple pipeline to convert the filtered CSCI class into ASP formatted rules and constraints. From this, we're able to run a basic constraint identifier that returns which classes conflict with one another. Additionally, we were able to set up two basic buttons that execute this "Run Filterer" and "Run Processor".

## Branches for Version 0.2

- origin/josh/test: mostly ASP/clingo related things I have been working on. Currently working on integrating some tests and bug fixes
- orign/andra-test2: Generate samples for more specific testing for JSON files
- origin/andra-testing(deleted): create web scraping script
- origin/frank_sand: Mainly JSON file development and DJango environment setup. Some ASP play files for figuring stuff out
- oring/dev: When we are working together (in person) or want to make sure we don't break main
- main: Main branch where working iteration is found and includes front-end development

## Version 1.0 release notes

### Clingo Changes

Updated the clingo files to identify and optimize based on total overlap.

We have conflict if: s1, s2 have overlapping day, time, and are different classes
We have overlap if every section in C1, C2 are in conflict -> no valid path
Overlaps are then weighted by group.

Current groups are based on the four year plan.

Group 1 includes all the classes predicted to take in year 1, Group 2 year 2, ...
Group 0 includes all classes not in the four year plan.

Current weights are set to 2 if in Group 1-4, 1 if in group 0. Can be adjusted as inputs.

Weighted overlap = W1 + W2, where W1 is the weight of class 1, W2 is the weight of class 2.

Minimize based on weighted overlap. Additionally, minimize number of changes to the input schedule (lower priority).

## Version 2.0 release notes

### More Clingo Changes

Updated the clingo files to identify and optimize based on critical sections.

Before with the notion of total overlap, we could only ever guarantee that any given 2 courses could be taken at the same time.

With the definition of critical sections, we can now guarantee that, for courses of the same year, you can at least take the critical sections at the same time for any number of classes.

- Removed weights based off classes in the four year plan
- All classes now have the same weight
- Only counting conflicts for classes of the same year
- Refactored clingo code to compute optimal answer sets quickly (in a matter of seconds rather than minutes)
- Added in logic to handle professor preferences

### Application Changes

All of the uploaded sections are stored in the database and are filtered to display on the dashboard. There are also generated pages to show details for all of the sections.

### Command Line Deployment Changes

To run the application from the command line after starting a virtual environment and installing the python packages

```{bash}
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata ./scheduleFunctions/fixtures/prepopulated.json
python manage.py runserver
```

### Docker Deployment Changes

To build the docker containter image, move to the root directory for the repository and run:

`sudo docker build -t capstone-14:latest .`

Run the container using:

`sudo docker run --name capstone-14 -p 80:8000 -d capstone-14`

This container is presented on port 80 (http). This is an unsecure connection and will give a warning when connecting.
This container is run in detached mode which will not provide any command line output.

To view the logs of the running container use:

`sudo docker logs capstone-14`

or:

`sudo docker logs capstone-14 | tail`
