% Include necessary files
#include "filtered.lp".
% #include "..\\testing\\test_cases\\test_case_00.lp".
#include "days.lp".
#include "overlap.lp".

% Assign one valid time slot to each section with a room and professor assigned
{ scheduled_section(C, S, E, D, R, P) : time_slot(S, E, D) } = 1 :- 
    section(C, _, _, _, _, _, R, P). 

% day_conflict(C1, C2) :- scheduled_section(C1, S1, E1, D1, R1, P1), scheduled_section(C2, S2, E2, D2, R2, P2), overlapping_days(D1, D2), C1 != C2.
% time_conflict(C1, C2) :- scheduled_section(C1, S1, E1, D1, R1, P1), scheduled_section(C2, S2, E2, D2, R2, P2), overlapping_times(S1, E1, S2, E2), C1 != C2.
scheduled_conflict(C1, C2) :- scheduled_section(C1, S1, E1, D1, R1, P1), scheduled_section(C2, S2, E2, D2, R2, P2), overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2), C1 != C2.

% #show scheduled_section/6.
% #show day_conflict/2.
% #show time_conflict/2.
#show scheduled_conflict/2.