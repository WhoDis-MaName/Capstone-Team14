% Include necessary files
#include "filtered.lp".
% #include "..\\testing\\test_cases\\test_case_00.lp".
#include "days.lp".
#include "overlap.lp".

% Assign one valid time slot to each section with a room and professor assigned
{ scheduled_section(C, S, E, D, R, P) : time_slot(S, E, D) } = 1 :- 
    section(C, _, _, _, _, _, R, P). 

% Ensure the scheduled section is also represented without room and professor
scheduled_section(C, S, E, D) :- scheduled_section(C, S, E, D, _, _). 

% Define conflicts based on overlapping days and times
new_conflict(C1, C2) :- 
    scheduled_section(C1, S1, E1, D1), 
    scheduled_section(C2, S2, E2, D2), 
    C1 != C2, 
    overlapping_days(D1, D2), 
    overlapping_times(S1, E1, S2, E2).

% Room conflicts: Two sections cannot be in the same room at the same time
:- scheduled_section(C1, S1, E1, D1, R, _), 
   scheduled_section(C2, S2, E2, D2, R, _), 
   new_conflict(C1, C2).

% Professor conflicts: A professor cannot teach two classes at the same time
:- scheduled_section(C1, S1, E1, D1, _, P), 
   scheduled_section(C2, S2, E2, D2, _, P), 
   new_conflict(C1, C2).

% Identify distinct true conflicts
new_true_conflict(C1, C2) :- 
    new_conflict(C1, C2), 
    not new_true_conflict(C2, C1).

% Count conflicts
new_conflict_count(N) :- N = #count{ C1, C2 : new_true_conflict(C1, C2) }.
conflict_count(N) :- N = #count{ C1, C2 : new_conflict(C1, C2) }.

% Debugging outputs
#show scheduled_section/6.
#show new_conflict/2.
#show new_true_conflict/2.
#show new_conflict_count/1.
