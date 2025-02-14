#const r = 2.
#const p = 2.
#const t = 2.
#const c = 2.

room(1..r).
professor(1..p).
time(1..t).

class(1..c).


% Goal: assign classes a time, room, and professor s.t. there is no or minimal overlap

% For each class, assign 1 time, room and professor
{ assignment(C, T, R, P) : time(T), room(R), professor(P)} = 1 :- class(C).

% { assignment(C, T, R) : time(T), room(R)} = 1 :- class(C).

% % It cannot be that there are two classes in the same room at the same time
:- assignment(C1, T1, R1, P1), assignment(C2, C2, R2, P2), T1 = T2, R1 = R2, C1!=C2.
% :- assignment(C1, T1, R1), assignment(C2, C2, R2), T1 = T2, R1 = R2, C1!=C2.

% % It cannot be that there are two classes in the same room at the same time
:- assignment(C1, T1, R1, P1), assignment(C2, C2, R2, P2), T1 = T2, P1 = P2, C1!=C2.

% Goal: identify conflicts between core classes. 

#show assignment/4.