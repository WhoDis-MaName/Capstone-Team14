#include "filtered.lp".
% #include "..\\testing\\test_cases\\test_case_00.lp".
#include "days.lp".
#include "overlap.lp".

% Example section from classes.lp:
% section("CSCI8700", "001", "15948", 18:00, 20:40, "W", "Peter Kiewit Institute 160", "Harvey Pe Siy").

% For each section with a room and professor already assigned, choose one timeslot.
% TODO: Add constraint so that only certain time slots are allowed based on number of credits. 
% For example, a 5 credit class must have mtwr
{scheduled_section(C, S, E, D, R, P) : time_slot(S, E, D) } = 1 :- section(C, _, _, _, _, _, R, P). 

% TODO: Add in weights to classes - default to 1 if nothing input from the user
% Once the classes have weights, we can assign weights to the conflicts s.t. 
% new_conflict(C1, C2, W) :- scheduled_section(C1, S1, E1, D1, W1), scheduled_section(C2, S2, E2, D2, W2), W = W1 + W2, ...
% and then the minimize function becomes: minimize{W, C1, C2 : new_true_conflict(C1, C2, W)}.
scheduled_section(C, S, E, D) :- scheduled_section(C, S, E, D, _, _). 

% new_conflict(C1, C2, S1, E1, S2, E2, D1, D2) :- scheduled_section(C1, S1, E1, D1), scheduled_section(C2, S2, E2, D2), C1!=C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2). %, not new_conflict(C2, C1). 
% new_conflict(C1, C2) :- new_conflict(C1, C2, _, _, _, _, _, _).

% It cannot be that there are two classes in the same room at the same time
:- scheduled_section(C1, S1, E1, D1, R1, P1), scheduled_section(C2, S2, E2, D2, R2, P2), new_conflict(C1, C2), R1 = R2. %, C1!=C2.

% It cannot be that there are two classes with the same professor at the same time
:- scheduled_section(C1, S1, E1, D1, R1, P1), scheduled_section(C2, S2, E2, D2, R2, P2), new_conflict(C1, C2), P1 = P2. %, C1!=C2.

% It cannot be that there are two sections that are not the same class that overlap. - this is already done in our definition of conflict.
% :- scheduled_section(C1, S1, E1, D1, R1, P1), scheduled_section(C2, S2, E2, D2, R2, P2), new_conflict(C1, C2), S1!=S2. % [1@3]

% #show scheduled_section/4.
new_conflict(C1, C2, S1, E1, S2, E2, D1, D2) :- scheduled_section(C1, S1, E1, D1), scheduled_section(C2, S2, E2, D2), C1!=C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2). 
new_conflict(C1, C2) :- new_conflict(C1, C2, _, _, _, _, _, _).

#show new_conflict/8.
% #show conflict/8.

new_true_conflict(C1, C2) :- new_conflict(C1, C2), new_conflict(C2, C1), not new_true_conflict(C2, C1).

new_conflict_count(N) :- N = #count{ C1, C2 : new_true_conflict(C1, C2) }.
conflict_count(N) :- N = #count{ C1, C2 : new_conflict(C1, C2) }.

% #show conflict_count/1.
#show new_conflict_count/1.
% #show scheduled_section/6.
#minimize{1, C1, C2 : new_true_conflict(C1, C2)}.