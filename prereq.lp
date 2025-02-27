% RULES AND CONSTRAINTS FOR COURSE PREREQUISITES
% IN ACADEMIC PLANNING USING ANSWER SET PROGRAMMING

% Defining Course and Student Relationships
% ----------------------

% A course exists in the system.
course(Course).

% A student exists in the system.
student(Student).

% A student has passed a specific course.
passed(Student, Course).

% A student is enrolled in a course.
enrolled(Student, Course).

% ----------------------
% Prerequisite Definitions
% ----------------------

% Single prerequisite: Course A requires Course B to be taken first.
prereq(Course, RequiredCourse).

% "OR" prerequisite: Course A requires one of multiple options.
prereq_or(Course, Option1, Option2).
prereq_or(Course, Option1, Option2, Option3).

% "AND" prerequisites: Course A requires multiple specific courses.
prereq(Course, Required1).
prereq(Course, Required2).

% "AND-OR" prerequisite: Course A requires two out of three options.
prereq_and_or(Course, {Option1, Option2, Option3}).

% Instructor permission as a prerequisite.
prereq(Course, instructor_permission).

% ----------------------
% Rules: Determining Eligibility to Take a Course
% ----------------------

% Rule 1: A student can take a course if it has no prerequisites.
can_take(Student, Course) :- course(Course), not prereq(Course, _).

% Rule 2: A student can take a course if they have passed all its required prerequisites.
can_take(Student, Course) :- prereq(Course, Prereq), passed(Student, Prereq).

% Rule 3: A student can take a course if they meet at least one "OR" prerequisite.
can_take(Student, Course) :- prereq_or(Course, Opt1, Opt2), (passed(Student, Opt1); passed(Student, Opt2)).
can_take(Student, Course) :- prereq_or(Course, Opt1, Opt2, Opt3), (passed(Student, Opt1); passed(Student, Opt2); passed(Student, Opt3)).

% Rule 4: A student can take a course if they meet all "AND" prerequisites.
can_take(Student, Course) :- prereq(Course, Prereq1), prereq(Course, Prereq2), passed(Student, Prereq1), passed(Student, Prereq2).

% Rule 5: A student can take a course if they meet at least two out of three options in an "AND-OR" prerequisite.
count_passed(Student, {Opt1, Opt2, Opt3}, Count) :-
    passed(Student, Opt1) + passed(Student, Opt2) + passed(Student, Opt3) >= Count.

can_take(Student, Course) :- prereq_and_or(Course, {Opt1, Opt2, Opt3}), count_passed(Student, {Opt1, Opt2, Opt3}, 2).

% Rule 6: A student can take a course if they have instructor permission.
can_take(Student, Course) :- prereq(Course, instructor_permission), has_permission(Student, Course).

% ----------------------
% Constraints: Prevent Enrollment if Requirements Are Not Met
% ----------------------

% Constraint 1: A student cannot enroll in a course if they haven't passed a required prerequisite.
:- enrolled(Student, Course), prereq(Course, Prereq), not passed(Student, Prereq).

% Constraint 2: A student cannot enroll if they don't meet at least one of the "OR" prerequisites.
:- enrolled(Student, Course), prereq_or(Course, Opt1, Opt2), not passed(Student, Opt1), not passed(Student, Opt2).

:- enrolled(Student, Course), prereq_or(Course, Opt1, Opt2, Opt3), not passed(Student, Opt1), not passed(Student, Opt2), not passed(Student, Opt3).

% Constraint 3: A student cannot enroll if they haven't passed all "AND" prerequisites.
:- enrolled(Student, Course), prereq(Course, Prereq), not passed(Student, Prereq).

% Constraint 4: A student cannot enroll in a course requiring two out of three prerequisites unless they have passed at least two.
:- enrolled(Student, Course), prereq_and_or(Course, {Opt1, Opt2, Opt3}), count_passed(Student, {Opt1, Opt2, Opt3}, Passed), Passed < 2.

% Constraint 5: A student cannot enroll in a course requiring instructor permission unless granted.
:- enrolled(Student, Course), prereq(Course, instructor_permission), not has_permission(Student, Course).

% ----------------------
% Queries to Check Course Eligibility
% ----------------------

% Query 1: Check which courses a student can take.
#show can_take/2.

% Query 2: Find missing prerequisites for a student.
missing_prereq(Student, Course, Prereq) :- prereq(Course, Prereq), not passed(Student, Prereq).
missing_one_of(Student, Course, Opt1, Opt2) :- prereq_or(Course, Opt1, Opt2), not passed(Student, Opt1), not passed(Student, Opt2).
missing_two_of(Student, Course, {Opt1, Opt2, Opt3}) :- prereq_and_or(Course, {Opt1, Opt2, Opt3}), count_passed(Student, {Opt1, Opt2, Opt3}, Passed), Passed < 2.

#show missing_prereq/3.
