% #include "filtered.lp".
#include "..\\testing\\test_cases\\test_case_00.lp".
% #include "..\\testing\\test_cases\\test_case_01.lp".
#include "fourYearPlanTest.lp".
#include "days.lp".
#include "overlap.lp".
#include "groups.lp".

% Example section from classes.lp:
% section("CSCI8700", "001", "15948", 18:00, 20:40, "W", "Peter Kiewit Institute 160", "Harvey Pe Siy").

% module for classes not in the four year plan
module(0, 0).
planned_course(C, 0, 0) :- class(C), not planned_classes(C). %, not planned_course(C).

#show class/1.

#show planned_course/3.

% section(C, I, S, E, D, M, Y, R, P) :- section(C, I, _, S, E, D, R, P), planned_course(C, M, Y), module(M, Y).

% #show section/9.

% For each section with a group, module, room, and professor already assigned, choose one timeslot.
% For example, a 5 credit class must have mtwr
% {scheduled_section(C, S, E, D, M, Y, R, P) : time_slot(S, E, D) } = 1 :- section(C, I, S, E, D, M, Y, R, P). 

% #show scheduled_section/8.

% TODO: Add in weights to classes - default to 1 if nothing input from the user
% % Once the classes have weights, we can assign weights to the conflicts s.t. 
% % scheduled_conflict(C1, C2, W) :- scheduled_section(C1, S1, E1, D1, W1), scheduled_section(C2, S2, E2, D2, W2), W = W1 + W2, ...
% % and then the minimize function becomes: minimize{W, C1, C2 : scheduled_true_conflict(C1, C2, W)}.
% scheduled_section(C, S, E, D) :- scheduled_section(C, S, E, D, M, Y, R, P).
% scheduled_section(C, S, E, D, R, P) :- scheduled_section(C, S, E, D, M, Y, R, P).

% % scheduled_conflict(C1, C2, S1, E1, S2, E2, D1, D2) :- scheduled_section(C1, S1, E1, D1), scheduled_section(C2, S2, E2, D2), C1!=C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2). %, not scheduled_conflict(C2, C1). 
% % scheduled_conflict(C1, C2) :- scheduled_conflict(C1, C2, _, _, _, _, _, _).

% % It cannot be that there are two classes in the same room at the same time
% % :- scheduled_section(C1, S1, E1, D1, R1, P1), scheduled_section(C2, S2, E2, D2, R2, P2), scheduled_conflict(C1, C2), R1 = R2. %, C1!=C2.

% % It cannot be that there are two classes with the same professor at the same time
% % :- scheduled_section(C1, S1, E1, D1, R1, P1), scheduled_section(C2, S2, E2, D2, R2, P2), scheduled_conflict(C1, C2), P1 = P2. %, C1!=C2.

% % It cannot be that there are two sections that are not the same class that overlap. - this is already done in our definition of conflict.
% % :- scheduled_section(C1, S1, E1, D1, R1, P1), scheduled_section(C2, S2, E2, D2, R2, P2), scheduled_conflict(C1, C2), S1!=S2. % [1@3]

% % #show scheduled_section/4.
% scheduled_conflict(C1, C2, S1, E1, S2, E2, D1, D2) :- scheduled_section(C1, S1, E1, D1), scheduled_section(C2, S2, E2, D2), C1!=C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2).
% % scheduled_conflict(C1, C2) :- scheduled_conflict(C1, C2, S1, E1, S2, E2, D1, D2).

% % #show scheduled_conflict/8.

% % % There exists at least some path between C1 and C2.
% % scheduled_path(C1, C2) :- scheduled_section(C1, S1, E1, D1), scheduled_section(C2, S2, E2, D2), not scheduled_conflict(C1, C2, S1, E1, S2, E2, D1, D2), C1!=C2.

% % % There are no paths between C1 and C2 -> total overlap.
% % scheduled_overlap(C1, C2) :- class(C1), class(C2), not scheduled_path(C1, C2), C1!=C2.

% % schedule_overlap_count(N) :- N = #count{ C1, C2 : scheduled_overlap(C1, C2)  }.
% % schedule_path_count(N) :- N = #count{ C1, C2 : scheduled_path(C1, C2)  }.
% scheduled_conflict_count(N) :- N = #count{ C1, C2 : scheduled_conflict(C1, C2, S1, E1, S2, E2, D1, D2) }.

% % % #show conflict_count/1.
% % #show schedule_overlap_count/1.
% % #show schedule_path_count/1.
% #show scheduled_conflict_count/1.
% % #show scheduled_section/6.
% % #minimize{1, C1, C2 : scheduled_true_conflict(C1, C2)}.