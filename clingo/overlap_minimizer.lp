% #include "filtered.lp".
% #include "..\\testing\\test_cases\\test_case_00.lp".
% #include "fourYearPlanTest.lp".
% #include "days.lp".
% #include "overlap.lp".
% #include "groups.lp".
#include "overlap_identifier.lp".

module(0, 0).
planned_course(C, 0, 0) :- class(C), not planned_classes(C).

% Example section from classes.lp:
% section("CSCI8700", "001", "15948", 18:00, 20:40, "W", "Peter Kiewit Institute 160", "Harvey Pe Siy").

input_section(C, I, N, R, P) :- section(C, I, N, _, _, _, R, P). 

% For each section with a room and professor already assigned, choose one timeslot.
% TODO: Add constraint so that only certain time slots are allowed based on number of credits. 
% For example, a 5 credit class must have mtwr
{scheduled_section(C, I, N, S, E, D, R, P) : time_slot(S, E, D) } = 1 :- input_section(C, I, N, R, P).

% It cannot be that there are two classes in the same room at the same time
:- scheduled_section(C1, _, _, S1, E1, D1, R1, P1), scheduled_section(C2, _, _, S2, E2, D2, R2, P2), scheduled_conflict(C1, C2), R1 = R2. %, C1!=C2.

% It cannot be that there are two classes with the same professor at the same time
:- scheduled_section(C1, _, _, S1, E1, D1, R1, P1), scheduled_section(C2, _, _, S2, E2, D2, R2, P2), scheduled_conflict(C1, C2), P1 = P2. %, C1!=C2.

% It cannot be that we generate a new schedule that has more overlap than the original schedule.
:- original_weighted_overlap_sum(N1), scheduled_weighted_overlap_sum(N2), N2>=N1.

scheduled_conflict(C1, C2, S1, E1, S2, E2, D1, D2) :- scheduled_section(C1, _, _, S1, E1, D1, _, _), scheduled_section(C2, _, _, S2, E2, D2, _, _), C1!=C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2). 

% There exists at least some scheduled_path between C1 and C2.
scheduled_path(C1, C2) :- scheduled_section(C1, _, _, S1, E1, D1, _, _), scheduled_section(C2, _, _, S2, E2, D2, _, _), not scheduled_conflict(C1, C2, S1, E1, S2, E2, D1, D2), C1!=C2.

% There are no scheduled_paths between C1 and C2 -> total overlap.
scheduled_overlap(C1, C2) :- class(C1), class(C2), not scheduled_path(C1, C2), C1!=C2.

% calculate the weight for each overlap
scheduled_weighted_overlap_sum(C1, C2, W) :- scheduled_overlap(C1, C2), planned_course(C1, _, Y1), planned_course(C2, _, Y2), weight(Y1, W1), weight(Y2, W2), W = W1 + W2.

scheduled_conflict(C1, C2) :- scheduled_conflict(C1, C2, _, _, _, _, _, _).
scheduled_overlap_count(N) :- N = #count{ C1, C2 : scheduled_overlap(C1, C2) }.
scheduled_conflict_count(N) :- N = #count{ C1, C2 : scheduled_conflict(C1, C2) }.

scheduled_weighted_overlap_sum(N) :- N = #sum{ W, C1, C2 : scheduled_weighted_overlap_sum(C1, C2, W) }.

% #show conflict_count/1.
% #show scheduled_conflict_count/1.
% #show scheduled_overlap_count/1.
% #show weighted_scheduled_conflict/1.
% #show scheduled_weighted_overlap_sum/1.
% #show scheduled_section/6.
#show scheduled_section/8.

#minimize{W, C1, C2 : scheduled_weighted_overlap_sum(C1, C2, W)}.
% Prioritized minimize functions, try to minimize overlaps, then minimize individual conflicts. 
% TODO: look into how long this takes
% #minimize{W@2, C1, C2 : scheduled_weighted_overlap_sum(C1, C2, W)}.
% #minimize{1@1, C1, C2 : scheduled_conflict(C1, C2)}.
% #minimize{scheduled_weighted_overlap_sum}.