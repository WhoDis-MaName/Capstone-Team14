#include "filtered.lp".
% #include "..\\testing\\test_cases\\test_case_00.lp".
#include "days.lp".
% #include "overlap.lp".

% 1 ary course
course(C) :- course(C, _, _).

% Example section from classes.lp:
% section("CSCI8700", "001", "15948", 18:00, 20:40, "W", "Peter Kiewit Institute 160", "Harvey Pe Siy").

% 4 ary section with course, start time, end time, and day
section(C, S, E, D) :- section(C, _, _, S, E, D, _, _).

overlapping_times(S1, E1, S2, E2) :- scheduled_section(C1, S1, E1, D1), scheduled_section(C2, S2, E2, D2), S1 <= E2, S2 <= E1.

% 2 ary time with start time and end time - independent of day.
% times(S, E) :- time_slot(S, E, _).


% For each section with a room and professor already assigned, choose one timeslot.
{scheduled_section(C, S, E, D, R, P) : time_slot(S, E, D) } = 1 :- section(C, _, _, _, _, _, R, P). 

new_conflict(C1, C2, S1, E1, S2, E2, D1, D2) :- scheduled_section(C1, S1, E1, D1), scheduled_section(C2, S2, E2, D2), C1!=C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2). %, not new_conflict(C2, C1). 
new_conflict(C1, C2) :- new_conflict(C1, C2, _, _, _, _, _, _).

% It cannot be that there are two classes in the same room at the same time
:- scheduled_section(C1, S1, E1, D1, R1, P1), scheduled_section(C2, S2, E2, D2, R2, P2), new_conflict(C1, C2), R1 = R2. %, C1!=C2.

% It cannot be that there are two classes with the same professor at the same time
:- scheduled_section(C1, S1, E1, D1, R1, P1), scheduled_section(C2, S2, E2, D2, R2, P2), new_conflict(C1, C2), P1 = P2. %, C1!=C2.

% It cannot be that there are two sections that are not the same class that overlap. - this is already done in our definition of conflict.
% :- scheduled_section(C1, S1, E1, D1, R1, P1), scheduled_section(C2, S2, E2, D2, R2, P2), new_conflict(C1, C2), S1!=S2. % [1@3]

% TODO: Add in weights to classes - default to 1 if nothing input from the user
% Once the classes have weights, we can assign weights to the conflicts s.t. 
% new_conflict(C1, C2, W) :- scheduled_section(C1, S1, E1, D1, W1), scheduled_section(C2, S2, E2, D2, W2), W = W1 + W2, ...
% and then the minimize function becomes: minimize{W, C1, C2 : new_true_conflict(C1, C2, W)}.
scheduled_section(C, S, E, D) :- scheduled_section(C, S, E, D, _, _). 

% #show scheduled_section/4.
new_conflict(C1, C2, S1, E1, S2, E2, D1, D2) :- scheduled_section(C1, S1, E1, D1), scheduled_section(C2, S2, E2, D2), C1!=C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2). %, not new_conflict(C2, C1). 
new_conflict(C1, C2) :- new_conflict(C1, C2, _, _, _, _, _, _).

#show new_conflict/8.

new_true_conflict(C1, C2) :- new_conflict(C1, C2), new_conflict(C2, C1), not new_true_conflict(C2, C1).

new_conflict_count(N) :- N = #count{ C1, C2 : new_true_conflict(C1, C2) }.

#show new_conflict_count/1.
% #minimize{1, C1, C2 : new_true_conflict(C1, C2)}.