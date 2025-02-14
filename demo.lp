#const r = 2.
#const p = 2.
#const t = 2.
#const c = 2.

room(1..r).
professor(1..p).
time(1..t).
class(1..c).


% Look into: https://github.com/potassco/clinguin

% ===================================================================================================================================

% Project description: 

% This project seeks to identify overlapping courses that students are likely to have to take 
% simultaneously and propose a new schedule without conflicts. The first step is to simply identify 
% time conflicts between classes which students are likely to take in the same semester. 
% The defition of an overlap includes the class being scheduled during the same time slot (same day and time, ie: T/Th) with: 
    % 1. the same professor
    % 2. the same room

% We can identify key classes as: 
    % 1. core CS classes (ie, CS II, theory of computation, data structures, etc.)
        % - some core classes require prereqs. In this case, it is ok for a class and it's prerequisite 
        %   to be at the same time as most students won't be taking both in the same semester.
    % 2. core concentration classes (ie, NLP, AI, game design, etc.)
    % 3. 4000 level classes in general (prioritize senors)

% For example, a senior with a computer science or AI degree may want to take both 
% Intro to AI and Machine Learning and Datamining in which the classes should be scheduled at 
% different times. 

% The second step is to suggest a potential reorganization, optimizing the class 
% list such that there is minimum conflict. This could be optimized in a few ways, either focusing on 
% minimum number of overlaps, or adding weights to senior level classes so seniors are able to graduate on time 
% while still taking the classes they want. 

% Finally, the third step is to coordinate the classes with the shuttle 
% schedule such that students shouldn’t need to wait for a shuttle. 

% ===================================================================================================================================

% Goal: assign classes a time, room, and professor s.t. there is no or minimal overlap

% For each class, assign 1 time, room and professor
{ assignment(C, T, R, P) : time(T), room(R), professor(P)} = 1 :- class(C).

% It cannot be that there are two classes in the same room at the same time
:- assignment(C1, T1, R1, P1), assignment(C2, C2, R2, P2), T1 = T2, R1 = R2, C1!=C2.

% It cannot be that there are two classes in the same room at the same time
:- assignment(C1, T1, R1, P1), assignment(C2, C2, R2, P2), T1 = T2, P1 = P2, C1!=C2.

#show assignment/4.