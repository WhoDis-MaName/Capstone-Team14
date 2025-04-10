% #include "filtered.lp".
% #include "..\\testing\\test_cases\\test_case_00.lp".
#include "fourYearPlanTest.lp".
#include "days.lp".
#include "overlap.lp".
#include "groups.lp".

module(0, 0).
planned_course(C, 0, 0) :- class(C), not planned_classes(C).

% Example section from classes.lp:
% section("CSCI8700", "001", "15948", 18:00, 20:40, "W", "Peter Kiewit Institute 160", "Harvey Pe Siy").

% For each section with a room and professor already assigned, choose one timeslot.
% TODO: Add constraint so that only certain time slots are allowed based on number of credits. 
% For example, a 5 credit class must have mtwr
{scheduled_section(C, I, N, S, E, D, R, P) : time_slot(S, E, D) } = 1 :- section(C, I, N, _, _, _, R, P). 

#show scheduled_section/8.

scheduled_section(C, S, E, D, R, P) :- scheduled_section(C, I, N, S, E, D, R, P).

% TODO: Add in weights to classes - default to 1 if nothing input from the user
% Once the classes have weights, we can assign weights to the conflicts s.t. 
% scheduled_conflict(C1, C2, W) :- scheduled_section(C1, S1, E1, D1, W1), scheduled_section(C2, S2, E2, D2, W2), W = W1 + W2, ...
% and then the minimize function becomes: minimize{W, C1, C2 : scheduled_true_conflict(C1, C2, W)}.
scheduled_section(C, S, E, D) :- scheduled_section(C, S, E, D, _, _). 

% scheduled_conflict(C1, C2, S1, E1, S2, E2, D1, D2) :- scheduled_section(C1, S1, E1, D1), scheduled_section(C2, S2, E2, D2), C1!=C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2). %, not scheduled_conflict(C2, C1). 
% scheduled_conflict(C1, C2) :- scheduled_conflict(C1, C2, _, _, _, _, _, _).

% It cannot be that there are two classes in the same room at the same time
:- scheduled_section(C1, S1, E1, D1, R1, P1), scheduled_section(C2, S2, E2, D2, R2, P2), scheduled_conflict(C1, C2), R1 = R2. %, C1!=C2.

% It cannot be that there are two classes with the same professor at the same time
:- scheduled_section(C1, S1, E1, D1, R1, P1), scheduled_section(C2, S2, E2, D2, R2, P2), scheduled_conflict(C1, C2), P1 = P2. %, C1!=C2.

% It cannot be that there are two sections that are not the same class that overlap. - this is already done in our definition of scheduled_conflict.
% :- scheduled_section(C1, S1, E1, D1, R1, P1), scheduled_section(C2, S2, E2, D2, R2, P2), scheduled_conflict(C1, C2), S1!=S2. % [1@3]


scheduled_conflict(C1, C2, S1, E1, S2, E2, D1, D2) :- scheduled_section(C1, S1, E1, D1), scheduled_section(C2, S2, E2, D2), C1!=C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2). 
scheduled_conflict(C1, C2) :- scheduled_conflict(C1, C2, _, _, _, _, _, _).

% #show scheduled_conflict/8.
% #show scheduled_conflict/8.

% There exists at least some scheduled_path between C1 and C2.
scheduled_path(C1, C2) :- scheduled_section(C1, S1, E1, D1), scheduled_section(C2, S2, E2, D2), not scheduled_conflict(C1, C2, S1, E1, S2, E2, D1, D2), C1!=C2.

% There are no scheduled_paths between C1 and C2 -> total overlap.
scheduled_overlap(C1, C2) :- class(C1), class(C2), not scheduled_path(C1, C2), C1!=C2.

overlap_weight(C1, C2, W) :- planned_course(C1, _, Y1), planned_course(C2, _, Y2), weight(Y1, W1), weight(Y2, W2), W = W1 + W2.
weighted_overlap(C1, C2, W) :- scheduled_overlap(C1, C2), planned_course(C1, _, Y1), planned_course(C2, _, Y2), weight(Y1, W1), weight(Y2, W2), W = W1 + W2.

% #show weighted_overlap/3.

% #show scheduled_path/2.
% #show overlap/2.

scheduled_overlap_count(N) :- N = #count{ C1, C2 : scheduled_overlap(C1, C2) }.
scheduled_conflict_count(N) :- N = #count{ C1, C2 : scheduled_conflict(C1, C2) }.

weighted_scheduled_overlap(N) :- N = #sum{ W, C1, C2 : weighted_overlap(C1, C2, W) }.

% course_count(N) :- N = #count{ C1, C2 : planned_course(C, M, Y) }.
% weighted_scheduled_conflict(N) :- N = #sum{ W, C1 : scheduled_conflict(C1, C2), overlap_weight(C1, C2, W) }.

% scheduled_conflict_count(N) :- N = #count{ C1, C2 : scheduled_true_conflict(C1, C2) }.
% scheduled_conflict_count(N) :- N = #count{ C1, C2 : scheduled_conflict(C1, C2) }.

% #show conflict_count/1.
% #show scheduled_conflict_count/1.
% #show scheduled_overlap_count/1.
% #show weighted_scheduled_conflict/1.
% #show weighted_scheduled_overlap/1.
#show scheduled_section/6.

#minimize{W, C1, C2 : weighted_overlap(C1, C2, W)}.
% Prioritized minimize functions, try to minimize overlaps, then minimize individual conflicts. 
% TODO: look into how long this takes
% #minimize{W@2, C1, C2 : weighted_overlap(C1, C2, W)}.
% #minimize{1@1, C1, C2 : scheduled_conflict(C1, C2)}.
% #minimize{weighted_scheduled_overlap}.