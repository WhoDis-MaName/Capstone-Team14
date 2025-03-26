% #include "filtered.lp".
#include "days.lp".
#include "overlap.lp".

% Example course from classes.lp:
% course("CSCI4830", "INTRODUCTN SOFTWARE ENGINEERNG", "-").

% Goal: Show when there is a conflict between two classes
% Day slot and time slots separate
% Time slots have start time and end time in minutes past midnight: ie: (60, 135) = (1:00am, 2:15 am)
% Day possibililtes are: MW, TR, M, T, W, R, F, MTWR
% Times are usually hour long windows, but can be longer if the class only meets once a week
conflict(C1, C2, S1, E1, S2, E2, D1, D2) :- section(C1, S1, E1, D1), section(C2, S2, E2, D2), C1!=C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2). %, not conflict(C2, C1). 
conflict(C1, C2) :- conflict(C1, C2, _, _, _, _, _, _).

% TODO: fix bug with duplicate conflicts
true_conflict(C1, C2) :- conflict(C1, C2), conflict(C2, C1), not true_conflict(C2, C1).

conflict_count(N) :- N = #count{ C1, C2 : conflict(C1, C2) }.
true_conflict_count(N) :- N = #count{ C1, C2 : true_conflict(C1, C2) }.
section_count(N) :- N = #count{ S : section(S) }.

% Test things :

% test(C1, C2) :- conflict(C1, C2). 
% define some classes that should conflict and see what happens

% #show section_count/1.
% #show section/4.
% #show conflict/8.
% #show duplicate/2.
% #show conflict_count/1.
#show true_conflict_count/1.