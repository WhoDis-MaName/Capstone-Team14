% classes.lp

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

% 1 ary course
course(C) :- course(C, _, _).

% Example section from classes.lp:
% section("CSCI8700", "001", "15948", 18:00, 20:40, "W", "Peter Kiewit Institute 160", "Harvey Pe Siy").

% 1 ary section
section(C) :- section(C, _, _, _, _, _, _).

% 4 ary section with course, start time, end time, and day
section(C, S, E, D) :- section(C, _, _, S, E, D, _, _).

% overlapping_days(D1, D2) :- 
%     day(D1), day(D2), day(D3), overlapping_days(D1, D3), overlapping_days(D2, D3).
overlapping_days(D1, D2) :- 
    day(D1), day(D2), D1 = D2. % Exact match

overlapping_times(S1, E1, S2, E2) :- section(C1, S1, E1, D1), section(C2, S2, E2, D2), S1 < E2, S2 < E1.
overlapping_times(S1, E1, S2, E2) :- section(C1, S1, E1, D1), section(C2, S2, E2, D2), S1 = S2.
% overlapping_times(S1, E1, S2, E2) :- S1 > E2, S2 > E1.

% Goal: Show when there is a conflict between two classes
% TODO: updated to handle time slots properly
% Time slots are of the form ("4:00PM - 5:15PM", "MW"), where you have a time and a day
% Day possibililtes are: MW, TR, M, T, W, R, F, MTWR
% Times are usually hour long windows, but can be longer if the class only meets once a week
conflict(C1, C2, S1, E1, S2, E2, D1, D2) :- section(C1, S1, E1, D1), section(C2, S2, E2, D2), C1!=C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2). 
conflict(C1, C2) :- conflict(C1, C2, _, _, _, _, _, _).


conflict_count(N) :- N = #count{ C1, C2 : conflict(C1, C2) }.
% section_count(N) :- N = #count{ C1, C2 : conflict(C1, C2) }.

% Test things :

% test(C1, C2) :- conflict(C1, C2). 
% define some classes that should conflict and see what happens

#show conflict/8.
#show conflict_count/1.