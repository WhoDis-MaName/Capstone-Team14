% #include "filtered.lp".

% Example course from classes.lp:
% course("CSCI4830", "INTRODUCTN SOFTWARE ENGINEERNG", "-").

day(m).
day(mw).
day(mwrf).
day(t).
day(tr).
day(w).
day(r).
day(f).

% Direct overlaps
overlapping_days(mw, m).
overlapping_days(mw, w).
overlapping_days(tr, t).
overlapping_days(tr, r).
overlapping_days(mtwr, mw).
overlapping_days(mtwr, tr).
overlapping_days(mtwr, m).
overlapping_days(mtwr, t).
overlapping_days(mtwr, w).
overlapping_days(mtwr, r).
overlapping_days(D1, D2) :- 
    day(D1), day(D2), D1 = D2. % Exact match

overlapping_days(D1, D2) :- overlapping_days(D2, D1). % Ensure all overlaps are bidirectional

% 1 ary course
course(C) :- course(C, _, _).

% Example section from classes.lp:
% section("CSCI8700", "001", "15948", 18:00, 20:40, "W", "Peter Kiewit Institute 160", "Harvey Pe Siy").

% 1 ary section
section(C) :- section(C, _, _, _, _, _, _, _).

% 4 ary section with course, start time, end time, and day
section(C, S, E, D) :- section(C, _, _, S, E, D, _, _).

overlapping_times(S1, E1, S2, E2) :- section(C1, S1, E1, D1), section(C2, S2, E2, D2), S1 <= E2, S2 <= E1.

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
% section_count(N) :- N = #count{ S : section(S) }.

% Test things :

% test(C1, C2) :- conflict(C1, C2). 
% define some classes that should conflict and see what happens

% #show section_count/1.
% #show section/4.
% #show conflict/8.
% #show duplicate/2.
#show conflict_count/1.
#show true_conflict_count/1.