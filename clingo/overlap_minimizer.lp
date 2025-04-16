% #include "filtered.lp".
% #include "..\\testing\\test_cases\\test_case_00.lp".
% #include "fourYearPlanTest.lp".
% #include "days.lp".
% #include "overlap.lp".
% #include "groups.lp".
#include "overlap_identifier.lp".

% planned_course(C, 1, 0) :- class(C), not planned_classes(C).

% Example section from classes.lp:
% section("CSCI8700", "001", "15948", 18:00, 20:40, "W", "Peter Kiewit Institute 160", "Harvey Pe Siy").

input_section(C, I, N, R, P) :- section(C, I, N, _, _, _, R, P). 

% For each section with a room and professor already assigned, choose one timeslot.
% TODO: Add constraint so that only certain time slots are allowed based on number of credits. 
% For example, a 5 credit class must have mtwr
% TODO update choice rule for better performance
% section_professor(S, P).
{scheduled_section(C, I, N, S, E, D, R, P) : time_slot(S, E, D) } = 1 :- input_section(C, I, N, R, P).

% It cannot be that there are two classes in the same room at the same time
:- scheduled_section(C1, _, _, S1, E1, D1, R, P1), scheduled_section(C2, _, _, S2, E2, D2, R, P2), scheduled_conflict(C1, C2). %, C1!=C2.

% It cannot be that there are two classes with the same professor at the same time
:- scheduled_section(C1, _, _, S1, E1, D1, R1, P), scheduled_section(C2, _, _, S2, E2, D2, R2, P), scheduled_conflict(C1, C2). %, C1!=C2.

% TODO: Ensure that new timeslots align with credit hours
% mtwr - have to stay mtwr
% what about 1 credit hour labs?

scheduled_conflict(C1, C2, S1, E1, S2, E2, D1, D2) :- scheduled_section(C1, _, _, S1, E1, D1, _, _), scheduled_section(C2, _, _, S2, E2, D2, _, _), C1!=C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2). 

% There exists at least some scheduled_path between C1 and C2.
% Non-conflicting classes, C1 and C2
scheduled_path(C1, C2) :- scheduled_section(C1, _, _, S1, E1, D1, _, _), scheduled_section(C2, _, _, S2, E2, D2, _, _), not scheduled_conflict(C1, C2, S1, E1, S2, E2, D1, D2), C1!=C2.

% There are no scheduled_paths between C1 and C2 -> total overlap.
% Overlap if all sections are in conflict
scheduled_overlap(C1, C2) :- class(C1), class(C2), not scheduled_path(C1, C2), C1!=C2.

% calculate the weight for each overlap
scheduled_weighted_overlap_sum(C1, C2, W1 + W2) :- scheduled_overlap(C1, C2), planned_course(C1, W1, Y1), planned_course(C2, W2, Y2).

scheduled_conflict(C1, C2) :- scheduled_conflict(C1, C2, _, _, _, _, _, _).
scheduled_weighted_conflict(C1, C2, W1 + W2) :- scheduled_conflict(C1, C2), planned_course(C1, W1, Y1), planned_course(C2, W2, Y2).
% scheduled_overlap_count(N) :- N = #count{ C1, C2 : scheduled_overlap(C1, C2) }.
% scheduled_conflict_count(N) :- N = #count{ C1, C2 : scheduled_conflict(C1, C2) }.

#show scheduled_section/8.

% It cannot be that we generate a new schedule that has more overlap than the original schedule.
% :- original_weighted_overlap_sum(N1), scheduled_weighted_overlap_sum(N2), N2>=N1.
:- original_weighted_overlap_sum(N1), N1 <= #sum{ W, C1, C2 : scheduled_weighted_overlap_sum(C1, C2, W) }.

% There is a shedule change between two section IDs if they are at different times or different days.
schedule_change(C, I) :- scheduled_section(C, I, N, S1, E1, D1, R, P), section(C, I, N, S2, E2, D2, R, P), S1 != S2, E1 != E2. 
schedule_change(C, I) :- scheduled_section(C, I, N, S1, E1, D1, R, P), section(C, I, N, S2, E2, D2, R, P), D1 != D2. 

% #minimize{W, C1, C2 : scheduled_weighted_overlap_sum(C1, C2, W)}.

% Prioritized minimize functions, try to minimize overlaps, then minimize individual conflicts. 
% TODO: look into how long this takes
#minimize{W@3, C1, C2 : scheduled_weighted_overlap_sum(C1, C2, W)}.
% TODO: should we minimize this based on weight or count them all the same?
#minimize{1@2, C, I : schedule_change(C, I)}.
% #minimize{scheduled_weighted_overlap_sum}.