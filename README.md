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
