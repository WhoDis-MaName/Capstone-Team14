#include "overlap_identifier_critical_sections.lp".

% Example section from classes.lp:
% section("CSCI8700", "001", "15948", 18:00, 20:40, "W", "Peter Kiewit Institute 160", "Harvey Pe Siy").


input_section(C, I, N, R, P) :- section(C, I, N, _, _, _, R, P). 

% TODO: Add constraint so that only certain time slots are allowed based on number of credits. 
% For example, a 5 credit class must have mtwr

% For each section with a room and professor already assigned, choose one timeslot.
% make it so that we only have one of the cross listed sections and then assign the other one manually
{scheduled_section_time_slot(N, S, E, D) : time_slot(S, E, D) } = 1 :- input_section(C, I, N, R, P), not true_cross_listed(_, N).

% Manually assign the same timeslot to cross listed classes
% Maybe leave it for python?
% scheduled_section_time_slot(N2, S, E, D) :- scheduled_section_time_slot(N, S, E, D), input_section(C2, I2, N2, R2, P2), true_cross_listed(N, N2).

% Obtain 8 arity section for the sake of return value
scheduled_section(C, I, N, S, E, D, R, P) :- input_section(C, I, N, R, P), scheduled_section_time_slot(N, S, E, D).

% Manually assign the same timeslot to cross listed courses
% scheduled_section(C, I, N2, S, E, D, R, P) :- true_cross_listed(N1, N2), input_section(C, I, N2, R, P), scheduled_section_time_slot(N1, S, E, D).

% The course C for a section number N
scheduled_section_course(C, N) :- input_section(C, I, N, R, P), scheduled_section_time_slot(N, S, E, D).


% The unique number identifier for a section
scheduled_section_number(N) :- scheduled_section_time_slot(N, S, E, D).

% The profressor P for a section number N
scheduled_section_professor(P, N) :- scheduled_section(C, I, N, S, E, D, R, P).

% The room R for a section number N
scheduled_section_room(R, N) :- scheduled_section(C, I, N, S, E, D, R, P).

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

% New global constraint, cross listed courses must be at the same time
% If our input sections are cross listed, we have to ensure our new scheduled sections in the exact same timeslot

% It cannot be that the count of cross listed sections without the same timeslot is greater than 0 (cross listed already assumes N1 != N2)
% i.e.: All cross listed sections must share the exact same timeslot
% :- #count{ 1: 
%         not same_scheduled_slot(N1, N2)
%     } > 0, 
%     scheduled_section_number(N1),
%     scheduled_section_number(N2),
%     cross_listed(N1, N2).

% :- #count{ 1: 
%         cross_listed(N1, N2),
%         not same_scheduled_slot(N1, N2)
%     } > 0, 
%     scheduled_section_number(N1), 
%     scheduled_section_number(N2).


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
    time_slot_overlap(S1, E1, D1, S2, E2, D2).

% Conflict between cs and non cs section
scheduled_conflict(N1, N2) :- 
    scheduled_section_time_slot(N1, S1, E1, D1), 
    non_cs_section_time(N2, S2, E2, D2), 
    scheduled_section_course(C1, N1), 
    non_cs_section_course(C2, N2), 
    N1 != N2, C1!= C2, 
    time_slot_overlap(S1, E1, D1, S2, E2, D2).

% There exists at least some non_ovlerapping_courses between C1 and C2.
% Non-conflicting classes, C1 and C2
non_ovlerapping_courses(C1, C2) :- scheduled_section_course(C1, N1), scheduled_section_course(C2, N2), not scheduled_conflict(N1, N2), C1!=C2.
non_ovlerapping_courses(C1, C2) :- scheduled_section_course(C1, N1), non_cs_section_course(C2, N2), not scheduled_conflict(N1, N2), C1!=C2.

% There are no non_ovlerapping_coursess between C1 and C2 -> total overlap.
% Overlap if all sections are in conflict
scheduled_overlapping_courses(C1, C2) :- scheduled_section_course(C1, _), scheduled_section_course(C2, _), not non_ovlerapping_courses(C1, C2), C1!=C2.
scheduled_overlapping_courses(C1, C2) :- scheduled_section_course(C1, _), non_cs_class(C2), not non_ovlerapping_courses(C1, C2), C1!=C2.

true_scheduled_overlapping_courses(C1, C2) :- scheduled_overlapping_courses(C1, C2), not true_scheduled_overlapping_courses(C2, C1).

% calculate the weight for each overlap
scheduled_weighted_overlap_sum(C1, C2, W1 + W2) :- true_scheduled_overlapping_courses(C1, C2), planned_course(C1, W1, Y1), planned_course(C2, W2, Y2).

% It cannot be that we generate a new schedule that has more overlap than the original schedule.
:- original_weighted_overlap_sum(N1), N1 <= #sum{ W, C1, C2 : scheduled_weighted_overlap_sum(C1, C2, W) }.

% There is a shedule change between two section IDs if they are at different times or different days.
schedule_change(C, I) :- scheduled_section_time_slot(N, S1, E1, D1), section(C, I, N, S2, E2, D2, R, P), S1 != S2, E1 != E2. 
schedule_change(C, I) :- scheduled_section_time_slot(N, S1, E1, D1), section(C, I, N, S2, E2, D2, R, P), D1 != D2. 

% There is a conflict between critical sections of planned courses in the 4 year plan
% scheduled_critical_conflict(C1, C2) :- critical_section(C1, N1), critical_section(C2, N2), scheduled_conflict(N1, N2), C1!=C2, same_year(C1, C2), planned_classes(C1), planned_classes(C2).
scheduled_critical_conflict(C1, C2) :- critical_section(C1, N1), critical_section(C2, N2), scheduled_conflict(N1, N2), C1!=C2, same_year(C1, C2).

#minimize{1@3, C1, C2 : scheduled_critical_conflict(C1, C2)}.
% Prioritized minimize functions, try to minimize overlaps, then minimize individual conflicts. 
#minimize{W@2, C1, C2 : scheduled_weighted_overlap_sum(C1, C2, W)}.
% TODO: should we minimize this based on weight or count them all the same?
#minimize{1@1, C, I : schedule_change(C, I)}.

#show scheduled_section/8.
% #show scheduled_conflict/2.