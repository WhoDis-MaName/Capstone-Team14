% classes.lp

% Example course from classes.lp:
% course("CSCI4830", "INTRODUCTN SOFTWARE ENGINEERNG", "-").

% 1 ary course
course(C) :- course(C, _, _).

% Example section from classes.lp:
% section("CSCI4850", "851", "21119", "TBA", "TBA", "Totally Online", "Praval Sharma").
% section("CSCI4300", "001", "16070", "4:00PM - 5:15PM", "MW", "Durham Science Center 104", "Fabio Torres Vitor").

% 1 ary section
section(C) :- section(C, _, _, _, _, _, _).

% 2 ary section with course and time
section(C, T) :- section(C, _, _, T, _, _, _).

% 3 ary section with course, time, and day
section(C, T, D) :- section(C, _, _, T, D, _, _).

% Goal: Show when there is a conflict between two classes
conflict(A, B) :- section(A, T1, D1), section(B, T2, D2), T1=T2, D1=D2, A!=B. 

#show conflict/2.