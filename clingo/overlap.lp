% 1 ary course
% course(C) :- course(C, _, _).

% Example section from classes.lp:
% section("CSCI8700", "001", "15948", 18:00, 20:40, "W", "Peter Kiewit Institute 160", "Harvey Pe Siy").

% 1 ary section
% section(C) :- section(C, _, _, _, _, _, _, _).

% 4 ary section with course, start time, end time, and day
section(C, S, E, D) :- section(C, _, _, S, E, D, _, _).
non_cs_section(C, S, E, D) :- non_cs_section(C, _, _, S, E, D, _, _).
% section(C, I, S, E, D) :- section(C, I, _, S, E, D, _, _).

overlapping_times(S1, E1, S2, E2) :- time_slot(S1, E1, _), time_slot(S2, E2, _), S1 <= E2, S2 <= E1.
% We have to make this a seperate case as non-cs classes have different timeslots
overlapping_times(S1, E1, S2, E2) :- time_slot(S1, E1, _), non_cs_time_slot(S2, E2, _), S1 <= E2, S2 <= E1.