#include "filtered.lp".
#include "days.lp".
#include "overlap.lp".


% 2 ary time with start time and end time - independent of day.
% times(S, E) :- time_slot(S, E, _).

% For each section, choose one timeslot.
{scheduled_section(C, S, E, D, P) : time_slot(S, E, D) } = 1 :- section(C, _, _, _, _, _, _, P). 
scheduled_section(C, S, E, D) :- scheduled_section(C, S, E, D, _). 

% #show scheduled_section/4.

% new_conflict(C1, C2, S1, E1, S2, E2, D1, D2) :- scheduled_section(C1, S1, E1, D1), scheduled_section(C2, S2, E2, D2), C1!=C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2). %, not conflict(C2, C1). 
% new_conflict(C1, C2) :- new_conflict(C1, C2, _, _, _, _, _, _).

% #show new_conflict/2.

% new_true_conflict(C1, C2) :- new_conflict(C1, C2), new_conflict(C2, C1), not new_true_conflict(C2, C1).

% new_conflict_count(N) :- N = #count{ C1, C2 : new_true_conflict(C1, C2) }.

% #show new_conflict_count/1.
% % #minimize{new_conflict_count}.