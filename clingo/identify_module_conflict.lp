#include "filtered.lp".
#include "fourYearPlan.lp".
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
conflict(C1, C2, S1, E1, S2, E2, D1, D2) :- section(C1, S1, E1, D1), section(C2, S2, E2, D2), C1!=C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2). %, not conflict(C2, C1). 
conflict(C1, C2) :- conflict(C1, C2, _, _, _, _, _, _).

% course is 3 ary predicate  with course, module, number of credits
section(C, I, S, E, D, M, Y) :- section(C, I, S, E, D), course(C, M, _), module(M, Y).
same_module(C1, C2) :- section(C1, I1, S1, E1, D1, M1, Y1), section(C2, I2, S2, E2, D2, M2, Y2), conflict(C1, C2, S1, E1, S2, E2, D1, D2), C1 != C2, M1 = M2.
same_year(C1, C2) :- section(C1, I1, S1, E1, D1, M1, Y1), section(C2, I2, S2, E2, D2, M2, Y2), conflict(C1, C2, S1, E1, S2, E2, D1, D2), C1 != C2, Y1 = Y2.

% There is conflict if we are different modules and same year. 
module_conflict(C1, C2, I1, I2, M1, M2, Y1) :- section(C1, I1, S1, E1, D1, M1, Y1), section(C2, I2, S2, E2, D2, M2, Y2), conflict(C1, C2, S1, E1, S2, E2, D1, D2), M1 != M2, Y1 = Y2.

% #show module_conflict/7.

% module_conflict(M1, M2) :- module_conflict(S1, S2, M1, M2, Y1).

% if there are no conflicts for every possible sections in the module.
not_module_conflict(M1, M2) :- section(C1, I1, S1, E1, D1, M1, Y1), section(C2, I2, S2, E2, D2, M2, Y2), not module_conflict(C1, C2, I1, I2, M1, M2, Y1), M1 != M2.

#show not_module_conflict/2.
% Every section in the modules overlap
% There does not exist a set of sections that are not in conflict.
module_overlap(M1, M2) :- module(M1, _), module(M2, _), not not_module_conflict(M1, M2), M1 != M2.

true_module_overlap(M1, M2) :- module_overlap(M1, M2), not true_module_overlap(M2, M1).

% #show module_overlap/2.
% #show true_module_overlap/2.

% module_overlap(M1, M2) :- module_conflict(C1, C2), module_conflict(C2, C1), not module_overlap(C2, C1).

% conflict_count(N) :- N = #count{ C1, C2 : conflict(C1, C2) }.
% module_overlap_count(N) :- N = #count{ C1, C2 : module_overlap(C1, C2) }.
% section_count(N) :- N = #count{ S : section(S) }.

% Test things :

% test(C1, C2) :- conflict(C1, C2). 
% define some classes that should conflict and see what happens

% #show section_count/1.
% #show section/4.
% #show conflict/8.
% #show duplicate/2.
% #show conflict_count/1.
% #show module_overlap_count/1.