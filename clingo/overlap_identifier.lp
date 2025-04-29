% #include "total_filtered.lp".
% #include "total_filtered_credit_hours.lp".
% #include "total_filtered_test_optimal.lp".
% #include "filtered_test.lp".
% #include "example_output.lp".
% #include "..\\testing\\test_cases\\test_case_mini_overlap.lp".
% #include "..\\testing\\test_cases\\test_case_critical_section.lp".
% #include "..\\testing\\test_cases\\test_minimize_distance.lp".
% #include "..\\testing\\test_cases\\test_cross_listed.lp".
% #include "..\\testing\\test_cases\\test_case_english.lp".
% #include "..\\testing\\test_cases\\test_case_01.lp".
% #include "..\\testing\\test_cases\\test_case_00.lp".
% #include "output.lp".
% #include "fourYearPlanTest.lp".
#include "fourYearPlan.lp".
#include "days.lp".
#include "overlap.lp".

time_slot(S, E, D) :- time_slot_credits(S, E, D, T).

critical_conflict(C1, C2) :- critical_section(C1, N1), critical_section(C2, N2), conflict(N1, N2), C1!=C2, same_year(C1, C2).

planned_course(C, W, Y) :- course_weight(C, W, Y), not planned_classes(C).

section_time(N, S, E, D) :- section(C, I, N, S, E, D, R, P).

section_course(C, N) :- section(C, I, N, S, E, D, R, P).

non_cs_section_time(N, S, E, D) :- non_cs_section(C, I, N, S, E, D, R, P).

non_cs_section_course(C, N) :- non_cs_section(C, I, N, S, E, D, R, P).

section_professor(P, N) :- section(C, I, N, S, E, D, R, P).

section_room(R, N) :- section(C, I, N, S, E, D, R, P).

% Example course from classes.lp:
% course("CSCI4830", "INTRODUCTN SOFTWARE ENGINEERNG", "-").

% Goal: Show when there is a conflict between two classes
% Day slot and time slots separate
% Time slots have start time and end time in minutes past midnight: ie: (60, 135) = (1:00am, 2:15 am)
% Day possibililtes are: MW, TR, M, T, W, R, F, MTWR
% Times are usually hour long windows, but can be longer if the class only meets once a week

% There is conflict if: 
% - there does not exist at least one section from each module from a group that does not have conflict
conflict(N1, N2) :- 
    section_time(N1, S1, E1, D1), 
    section_time(N2, S2, E2, D2), 
    section_course(C1, N1), 
    section_course(C2, N2), 
    N1 != N2, C1!= C2, 
    time_slot_overlap(S1, E1, D1, S2, E2, D2),
    not cross_listed(N1, N2).

% Additionally, there is conflict between CS sections and non-CS sections. 
conflict(N1, N2) :- 
    section_time(N1, S1, E1, D1), 
    non_cs_section_time(N2, S2, E2, D2), 
    section_course(C1, N1), 
    non_cs_section_course(C2, N2), 
    time_slot_overlap(S1, E1, D1, S2, E2, D2).

% There exists at least some path between C1 and C2.
% non-conflicting classes
path(C1, C2) :- section_course(C1, N1), section_course(C2, N2), not conflict(N1, N2), C1!=C2.
% There is also a path between non_cs sections and cs_sections
path(C1, C2) :- section_course(C1, N1), non_cs_section_course(C2, N2), not conflict(N1, N2).

% There are no paths between C1 and C2 -> total overlap.
overlap(C1, C2) :- class(C1), class(C2), not path(C1, C2), C1!=C2.
overlap(C1, C2) :- class(C1), non_cs_class(C2), not path(C1, C2).

true_overlap(C1, C2) :- overlap(C1, C2), not true_overlap(C2, C1).

weighted_overlap(C1, C2, W1 + W2) :- true_overlap(C1, C2), planned_course(C1, W1, Y1), planned_course(C2, W2, Y2).

same_year(C1, C2) :- course_weight(C1, W1, Y), course_weight(C2, W2, Y). %, C1 != C2.
% Count 4000/8000 cross listed courses as the same year
% ie, csci8156 graph theory is cross listed with csci4500 so count csci8156 as both year 4 and year 5 (grad class).
same_year(C1, C2) :- cross_listed(N1, N2), section_course(C1, N1), section_course(C3, N2), same_year(C2, C3). %, C1 != C2.

original_weighted_overlap_sum(N) :- N = #sum{ W, C1, C2 : weighted_overlap(C1, C2, W), same_year(C1, C2) }.

% Check for overlap in rooms or in professor schedules
overlapping_room(N1, N2, R):- section_time(N1, S1, E1, D1), section_time(N2, S2, E2, D2), section_room(R, N1), section_room(R, N2), conflict(N1, N2). 
overlapping_prof(N1, N2, P):- section_time(N1, S1, E1, D1), section_time(N2, S2, E2, D2), section_professor(P, N1), section_professor(P, N2), conflict(N1, N2). 

% We can infer that two classes are cross listed if they have the exact same start time, end time, day, room, and professor
cross_listed(N1, N2) :- section(C1, I1, N1, S, E, D, R, P), section(C2, I2, N2, S, E, D, R, P), C1 != C2, N1 != N2.
true_cross_listed(N1, N2) :- cross_listed(N1, N2) , not true_cross_listed(N2, N1).