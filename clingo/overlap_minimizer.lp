% #include "overlap_identifier.lp".
% #include "total_filtered.lp".
#include "fourYearPlan.lp".
#include "days.lp".
#include "overlap.lp".

% SECTION PARSE INPUT 
time_slot(S, E, D) :- time_slot_credits(S, E, D, T).

section_course(C, N) :- section(C, I, N, S, E, D, R, P).

non_cs_section_time(N, S, E, D) :- non_cs_section(C, I, N, S, E, D, R, P).

non_cs_section_course(C, N) :- non_cs_section(C, I, N, S, E, D, R, P).

same_year(C1, C2) :- course_weight(C1, W1, Y), course_weight(C2, W2, Y), C1 != C2. 
same_year(C1, C2) :- cross_listed(N1, N2), section_course(C1, N1), section_course(C3, N2), same_year(C2, C3), C1 != C2.

cross_listed(N1, N2) :- section(C1, I1, N1, S, E, D, R, P), section(C2, I2, N2, S, E, D, R, P), C1 < C2, N1 != N2.

% Example section from classes.lp:
% section("CSCI8700", "001", "15948", 18:00, 20:40, "W", "Peter Kiewit Institute 160", "Harvey Pe Siy").

input_section(C, I, N, R, P, T) :- section(C, I, N, S, E, D, R, P), time_slot_credits(S, E, D, T). 

% Choose 1 section from each course to be "critical"
{ critical_section(C, N) : section_course(C, N) } = 1 :- class(C). 
{ critical_section(C, N) : non_cs_section_course(C, N)} = 1 :- non_cs_class(C). 

% For each section with a room and professor already assigned, choose one timeslot.
% make it so that we only have one of the cross listed sections and then assign the other one manually
% Also only assign time slots that are for the same credit hours. 
{scheduled_section_time_slot(N, S, E, D) : time_slot_credits(S, E, D, T) } = 1 :- input_section(C, I, N, R, P, T), not cross_listed(_, N).

% Manually assign the same timeslot to cross listed classes
% Maybe leave it for python?
% scheduled_section_time_slot(N2, S, E, D) :- scheduled_section_time_slot(N, S, E, D), input_section(C2, I2, N2, R2, P2, _), true_cross_listed(N, N2).

% Obtain 8 arity section for the sake of return value
scheduled_section(C, I, N, S, E, D, R, P) :- input_section(C, I, N, R, P, T), scheduled_section_time_slot(N, S, E, D).

% The course C for a section number N
scheduled_section_course(C, N) :- input_section(C, I, N, R, P, T), scheduled_section_time_slot(N, S, E, D).

% The unique number identifier for a section
scheduled_section_number(N) :- scheduled_section_time_slot(N, S, E, D).

% The profressor P for a section number N
scheduled_section_professor(P, N) :- section(C, I, N, S, E, D, R, P).

% The room R for a section number N
scheduled_section_room(R, N) :- section(C, I, N, S, E, D, R, P).

% It cannot be that there are two classes in the same room at the same time unless they are cross listed
% Greater than 1 because it sees itself
:- #count{ N: 
        scheduled_section_room(R, N), 
        scheduled_section_time_slot(N, S1, E1, D1),
        time_slot_overlap(S1, E1, D1, S2, E2, D2),
        not cross_listed(N, N2)
    } > 1, 
    room(R), 
    scheduled_section_time_slot(N2, S2, E2, D2).

% It cannot be that there are two classes with the same professor at the same time unless they are cross listed
% Greater than 1 because it sees itself
:- #count{ N: 
        scheduled_section_professor(P, N), 
        scheduled_section_time_slot(N, S1, E1, D1),
        time_slot_overlap(S1, E1, D1, S2, E2, D2),
        not cross_listed(N, N2)
    } > 1, 
    professor(P), 
    scheduled_section_time_slot(N2, S2, E2, D2).

% Same time slot, room, and professor
% same_scheduled_slot(N1, N2) :- scheduled_section(C1, I1, N1, S, E, D, R, P), scheduled_section(C2, I2, N2, S, E, D, R, P), N1 != N2, C1 != C2.

% TODO: Ensure that new timeslots align with credit hours
% mtwr - have to stay mtwr
% what about 1 credit hour labs?

% Conflict between 2 cs section
% There is conflict if:
%   They are not sections of the same course or cross listed courses
%   They have overlapping times and overlapping days
scheduled_conflict(N1, N2) :- 
    scheduled_section_time_slot(N1, S1, E1, D1), 
    scheduled_section_time_slot(N2, S2, E2, D2), 
    scheduled_section_course(C1, N1), 
    scheduled_section_course(C2, N2), 
    not cross_listed(N1, N2),
    N1 != N2, C1!= C2, 
    time_slot_overlap(S1, E1, D1, S2, E2, D2),
    same_year(C1, C2).

% Conflict between cs and non cs section
scheduled_conflict(N1, N2) :- 
    scheduled_section_time_slot(N1, S1, E1, D1), 
    non_cs_section_time(N2, S2, E2, D2), 
    scheduled_section_course(C1, N1), 
    non_cs_section_course(C2, N2), 
    N1 != N2, C1!= C2, 
    time_slot_overlap(S1, E1, D1, S2, E2, D2),
    same_year(C1, C2).

% There is a shedule change between two section IDs if they are at different times or different days.
schedule_change(C, I) :- scheduled_section_time_slot(N, S1, E1, D1), section(C, I, N, S2, E2, D2, R, P), (S1, E1, D1) != (S2, E2, D2). 
% There is a conflict between critical sections of planned courses in the 4 year plan
scheduled_critical_conflict(C1, C2) :- critical_section(C1, N1), critical_section(C2, N2), scheduled_conflict(N1, N2), C1!=C2.

% Prioritized minimize functions, first ensure the critical sections are available
#minimize{1@3, C1, C2 : scheduled_critical_conflict(C1, C2)}.
% Then minimize changes from original schedule
#minimize{1@1, C, I : schedule_change(C, I)}.

% #show scheduled_section_time_slot/4.
#show scheduled_section/8.
#show critical_section/2.

% Can do: opt = 3 for 3 possibilities
% Add possibilies about when to have courses

% TODO: add possibilites about when to have courses
%       ie: flag to keep morning classes in the morning, mw only, tr only, maybe schedule professors back to back
%           
% TODO: filter cross listed courses and add them back in at the end, check with user if correct, handle non-cs cross listed courses

% put constraints in natural language in requirements document -> paper by vlad about programming with achievements