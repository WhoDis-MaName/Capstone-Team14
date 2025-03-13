# Course Schedule Optimization

## Project Overview

This project aims to identify overlapping courses that students are likely to take simultaneously and propose a new schedule without conflicts. The main objectives include:

1. **Identifying time conflicts** between classes commonly taken in the same semester.
2. **Optimizing the schedule** to minimize conflicts and prioritize key courses.
3. **Coordinating the schedule with shuttle timings** to reduce student wait times.

---

## Identifying Course Overlaps

A course overlap is defined as a scheduling conflict where two classes occur during the same time slot (same day and time, e.g., Tuesday/Thursday) under the following conditions:

1. **Strict Overlap**

   - The same time **and** the same day **and** either:
     - The same professor, or
     - The same room.
   - At least one class should remain conflict-free if multiple sections exist.

2. **Handling Multiple Sections**
   - If multiple sections of a class are available (e.g., "AI" taught by different professors), should we ensure at least one section remains conflict-free, or that all sections avoid conflicts with other courses?

---

## Key Classes to Prioritize

Certain courses should be given priority when resolving conflicts:

1. **Core CS Courses**

   - Examples: Calculus I, CS II, Intro to Proofs, Discrete Math, Theory of Computation, Computer Networks, Software Engineering.
   - Classes with prerequisites can overlap with their prerequisite courses since students typically won't take both in the same semester.

2. **Core Concentration Classes**

   - Examples: NLP, AI, Game Design.

3. **4000-Level Courses** (Priority for seniors)
   - Ensuring upper-level students can take required courses without conflicts.

**Example Case:**
A senior pursuing a Computer Science or AI degree may need both _Intro to AI_ and _Machine Learning & Data Mining_. These courses should not be scheduled at the same time.

---

## Optimization Approach

After identifying conflicts, the next step is to suggest a reorganized schedule with minimal conflicts. The optimization criteria include:

- **Minimizing the number of overlapping classes.**
- **Prioritizing senior-level courses** to ensure timely graduation.
- **Considering different optimization strategies:**
  - Reducing overall conflicts.
  - Assigning weights to courses to prioritize essential ones.

---

## Coordinating with Shuttle Schedule

The final step involves aligning the course schedule with the university’s shuttle service to minimize student wait times.

---

## Additional Optimization Considerations

- A secondary **Answer Set Programming (ASP) model** will take the optimized schedule and refine it further with minimal disruption.
- Weak constraints can have different weights to reflect course importance.
- **TODO:** Read more on soft constraints and optimization techniques.

---

## Future Improvements

- Fine-tune soft constraints and optimization approaches.
- Gather feedback from students and faculty to refine scheduling priorities.
- Explore additional factors such as professor availability and classroom constraints.

---

## Conclusion

This project provides an optimized class schedule by reducing conflicts, prioritizing key courses, and considering shuttle coordination. The optimization process balances multiple factors to ensure students can take the courses they need without unnecessary scheduling conflicts.

## Release Notes Version 1.3

To run the project, simply launch your virtual environment using:

`source myenv/bin/activate`

After entering virtual environment, download Django:

`pip install -r requirements.txt`

Also Following the steps to install Clingo:

<https://github.com/potassco/clingo?tab=readme-ov-file>

To Launch the current iteration of project, use this command:

`python manage.py runserver`

- This release has mainly included a foundation for each section(front-end, back-end, and ASP). We've created basic python scripts for parsing through the schedule JSON file and a simple pipeline to convert the filtered CSCI class into ASP formatted rules and constraints. From this, we're able to run a basic constraint identifier that returns which classes conflict with one another. Additionally, we were able to set up two basic buttons that execute this "Run Filterer" and "Run Processor".

To launch django tests, use this command:

`python manage.py test`

## Branches for Version 1.3

- origin/josh/test: Josh and Andra worked on some pytest implementations
- orign/andra-test2: Test the django testing suite

## Release Notes Version 0.9

To run the project, simply launch your virtual environment using:

`source myenv/bin/activate`

After entering virtual environment, download Django:

`pip install django`

Also Following the steps to install Clingo:

<https://github.com/potassco/clingo?tab=readme-ov-file>

To Launch the current iteration of project, use this command:

`python manage.py runserver`

- This release has mainly included a foundation for each section(front-end, back-end, and ASP). We've created basic python scripts for parsing through the schedule JSON file and a simple pipeline to convert the filtered CSCI class into ASP formatted rules and constraints. From this, we're able to run a basic constraint identifier that returns which classes conflict with one another. Additionally, we were able to set up two basic buttons that execute this "Run Filterer" and "Run Processor".

## Branches for Version 0.9

- origin/josh/test:  mostly ASP/clingo related things I have been working on. Currently working on integrating some tests and bug fixes
- orign/andra-test2: Generate samples for more specific testing for JSON files
- origin/andra-testing(deleted):  create web scraping script
- origin/frank_sand: Mainly JSON file development and DJango environment setup. Some ASP play files for figuring stuff out
- oring/dev: When we are working together (in person) or want to make sure we don't break main
- main: Main branch where working iteration is found and includes front-end development
