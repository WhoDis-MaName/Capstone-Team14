% #include "filtered.lp".
#include "..\\testing\\test_cases\\test_case_01.lp".
#include "fourYearPlanTest.lp".
#include "days.lp".
#include "overlap.lp".

% Example course from classes.lp:
% course("CSCI4830", "INTRODUCTN SOFTWARE ENGINEERNG", "-").

% Goal: Show when there is a conflict between two classes
% Day slot and time slots separate
% Time slots have start time and end time in minutes past midnight: ie: (60, 135) = (1:00am, 2:15 am)
% Day possibililtes are: MW, TR, M, T, W, R, F, MTWR
% Times are usually hour long windows, but can be longer if the class only meets once a week

% There is conflict if: 
% - there does not exist at least one section from each module from a group that does not have conflict
conflict(C1, C2, S1, E1, S2, E2, D1, D2) :- section(C1, S1, E1, D1), section(C2, S2, E2, D2), C1!=C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2).
conflict(C1, C2) :- conflict(C1, C2, _, _, _, _, _, _).

% TODO: make modules for each lvl of class, ie 1000, 2000, 3000, or 4000 lvl class
module(0, 0).
planned_course(C, 0, 0) :- class(C), not planned_classes(C). %, not planned_course(C).

% course is 3 ary predicate  with course, module, number of credits
section(C, I, S, E, D, M, Y) :- section(C, I, S, E, D), planned_course(C, M, _), module(M, Y).

% There is conflict if we are different modules and same year. 
group_conflict(C1, C2, I1, I2, M1, M2, Y1) :- section(C1, I1, S1, E1, D1, M1, Y1), section(C2, I2, S2, E2, D2, M2, Y2), conflict(C1, C2, S1, E1, S2, E2, D1, D2), M1 != M2, Y1 = Y2.

true_group_conflict(C1, C2) :- group_conflict(C1, C2, I1, I2, M1, M2, Y1), not true_group_conflict(C2, C1).

true_group_conflict_count(N) :- N = #count{ C1, C2 : true_group_conflict(C1, C2) }.
conflict_count(N) :- N = #count{ C1 : conflict(C1, C2) }.
group_conflict_count(N) :- N = #count{ C1, C2 : group_conflict(C1, C2, I1, I2, M1, M2, Y1) }.

#show true_group_conflict_count/1.
#show group_conflict_count/1.
#show conflict_count/1.

% #show module_overlap/2.
#show true_group_conflict/2.
#show section/7.