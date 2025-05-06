% #include "total_filtered.lp".
% #include "total_filtered_test_optimal.lp".
% #include "filtered_test.lp".
% #include "example_output.lp".
% #include "..\\testing\\test_cases\\total_filtered_test_optimal.lp".
% #include "..\\testing\\test_cases\\test_case_mini_overlap.lp".
% #include "..\\testing\\test_cases\\test_case_critical_section.lp".
% #include "..\\testing\\test_cases\\test_minimize_distance.lp".
% #include "..\\testing\\test_cases\\test_cross_listed.lp".
% #include "..\\testing\\test_cases\\test_case_english.lp".
% #include "..\\testing\\test_cases\\test_case_01.lp".
% #include "..\\testing\\test_cases\\test_case_00.lp".
% #include "output.lp".
% #include "fourYearPlanTest.lp".
% #include "small_filtered.lp".
#include "fourYearPlan.lp".
#include "days.lp".
#include "overlap.lp".

time_slot(S, E, D) :- time_slot_credits(S, E, D, T).

% planned_course(C, W, Y) :- course_year(C, Y), not planned_classes(C).

section_time(N, S, E, D) :- section(C, I, N, S, E, D, R, P).

section_course(C, N) :- section(C, I, N, S, E, D, R, P).

non_cs_section_time(N, S, E, D) :- non_cs_section(C, I, N, S, E, D, R, P).

non_cs_section_course(C, N) :- non_cs_section(C, I, N, S, E, D, R, P).

section_professor(P, N) :- section(C, I, N, S, E, D, R, P).

section_room(R, N) :- section(C, I, N, S, E, D, R, P).

{ critical_section(C, N) : section_course(C, N) } = 1 :- class(C). 
{ critical_section(C, N) : non_cs_section_course(C, N)} = 1 :- non_cs_class(C). 

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

critical_conflict(C1, C2) :- critical_section(C1, N1), critical_section(C2, N2), conflict(N1, N2), C1!=C2, same_year(C1, C2).

same_year(C1, C2) :- course_year(C1, Y), course_year(C2, Y). %, C1 != C2.
% Count 4000/8000 cross listed courses as the same year
% ie, csci8156 graph theory is cross listed with csci4500 so count csci8156 as both year 4 and year 5 (grad class).
same_year(C1, C2) :- cross_listed(N1, N2), section_course(C1, N1), section_course(C3, N2), same_year(C2, C3). %, C1 != C2.
same_year(C1, C2) :- cross_listed(N2, N1), section_course(C1, N1), section_course(C3, N2), same_year(C2, C3). %, C1 != C2.

% C1 is an undergrad course, c2 is a grad course, c3 is an undergrad course
same_year(C2, C3) :- cross_listed(N1, N2), section_course(C1, N1), section_course(C2, N2), same_year(C1, C3).

% We can infer that two classes are cross listed if they have the exact same start time, end time, day, room, and professor
cross_listed(N1, N2) :- section(C1, I1, N1, S, E, D, R, P), section(C2, I2, N2, S, E, D, R, P), C1 < C2, N1 != N2.

#minimize{1, C1, C2 : critical_conflict(C1, C2)}.

original_critical_conflict_count(N) :- N = #count{1, C1, C2 : critical_conflict(C1, C2)}.

#show original_critical_conflict_count/1.
% #show critical_conflict/2.
% #show cross_listed/2.
% #show same_year/2.