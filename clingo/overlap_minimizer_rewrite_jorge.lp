% #include "filtered.lp".
% #include "..\\testing\\test_cases\\test_case_00.lp".
% #include "fourYearPlanTest.lp".
% #include "days.lp".
% #include "overlap.lp".
% #include "groups.lp".
% #include "overlap_identifier.lp".
#include "overlap_identifier_rewrite.lp".

% planned_course(C, 1, 0) :- class(C), not planned_classes(C).

% Example section from classes.lp:
% section("CSCI8700", "001", "15948", 18:00, 20:40, "W", "Peter Kiewit Institute 160", "Harvey Pe Siy").

input_section(C, I, N, R, P) :- section(C, I, N, _, _, _, R, P). 

% For each section with a room and professor already assigned, choose one timeslot.
% TODO: Add constraint so that only certain time slots are allowed based on number of credits. 
% For example, a 5 credit class must have mtwr
% TODO update choice rule for better performance
% section_professor(S, P).
% {scheduled_section(C, I, N, S, E, D, R, P) : time_slot(S, E, D) } = 1 :- input_section(C, I, N, R, P).
{scheduled_section_time_slot(N, S, E, D) : time_slot(S, E, D) } = 1 :- input_section(C, I, N, R, P).

% scheduled_section_time_slot(N, S, E, D) :- scheduled_section(C, I, N, S, E, D, R, P).
scheduled_section(C, I, N, S, E, D, R, P) :- input_section(C, I, N, R, P), scheduled_section_time_slot(N, S, E, D).

% scheduled_section_course(C, N) :- scheduled_section(C, I, N, S, E, D, R, P).
<<<<<<< HEAD:clingo/overlap_minimizer_rewrite.lp
% 
scheduled_section_course(C, N) :- input_section(C, I, N, R, P), scheduled_section_time_slot(N, S, E, D).
=======
scheduled_section_course(C, N) :- input_section(C, I, N, R, P).
>>>>>>> d79988f528f918b455e0fddb541282e8fb355a1b:clingo/overlap_minimizer_rewrite_jorge.lp

% The profressor P for a schedule number N
scheduled_section_professor(P, N) :- input_section(C, I, N, R, P).

scheduled_section_room(R, N) :- input_section(C, I, N, R, P).

% It cannot be that there are two classes in the same room at the same time
% :- scheduled_section(C1, _, _, S1, E1, D1, R, P1), scheduled_section(C2, _, _, S2, E2, D2, R, P2), scheduled_conflict(C1, C2). %, C1!=C2.
% :- scheduled_section_room(R, N1), 
%    scheduled_section_room(R, N2), 
%    scheduled_conflict(N1, N2). %, C1!=C2.

time_slot_overlap(S1, E1, DS1, S2, E2, DS2) :- 
    time_slot(S1, E1, DS1), 
    time_slot(S2, E2, DS2), 
    day_slot(DS1, D), day_slot(DS2, D),
    S1 <= E2, S2 <= E1.

:- #count{ N: 
        scheduled_section_room(R, N), 
        scheduled_section_time_slot(N, S1, E1, D1),
        time_slot_overlap(S1, E1, D1, S2, E2, D2)
    } > 1, 
    room(R), 
    time_slot(S2, E2, D2).

% It cannot be that there are two classes with the same professor at the same time
% :- scheduled_section(C1, _, _, S1, E1, D1, R1, P), scheduled_section(C2, _, _, S2, E2, D2, R2, P), scheduled_conflict(C1, C2). %, C1!=C2.
:- scheduled_section_time_slot(N1, S1, E1, D1), scheduled_section_time_slot(N2, S2, E2, D2), scheduled_section_professor(P, N1), scheduled_section_professor(P, N2), scheduled_conflict(N1, N2). %, C1!=C2.

% TODO: Ensure that new timeslots align with credit hours
% mtwr - have to stay mtwr
% what about 1 credit hour labs?

<<<<<<< HEAD:clingo/overlap_minimizer_rewrite.lp
scheduled_conflict(N1, N2) :- scheduled_section_time_slot(N1, S1, E1, D1), 
                                scheduled_section_time_slot(N2, S2, E2, D2), 
                                scheduled_section_course(C1, N1), 
                                scheduled_section_course(C2, N2), 
                                N1 != N2, C1!= C2, 
                                overlapping_days(D1, D2), 
                                overlapping_times(S1, E1, S2, E2).
                                
scheduled_conflict(N1, N2) :- scheduled_section_time_slot(N1, S1, E1, D1), non_cs_section_time(N2, S2, E2, D2), scheduled_section_course(C1, N1), non_cs_section_course(C2, N2), N1 != N2, C1!= C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2).
=======
scheduled_section_day(N, D) :- scheduled_section_time_slot(N, _, _, DS), day_slot(DS, D).
scheduled_section_time(N, S, E) :- scheduled_section_time_slot(N, S, E, _).

% non_overlap(C1, C2) :- 
%     class(C1), 
%     class(C2), 
%     #count{N1, N2: 
%         scheduled_section_course(C1, N1), 
%         scheduled_section_time_slot(N1, S1, E1, D1),
%         scheduled_section_course(C2, N2),
%         scheduled_section_time_slot(N2, S2, E2, D2),
%         not time_slot_overlap(S1, E1, D1, S2, E2, D2)
%     } >= 1.

% scheduled_conflict(N1, N2) :-
%     scheduled_section_time_slot(N1, S1, E1, D1), 
%     scheduled_section_time_slot(N2, S2, E2, D2), 
%     scheduled_section_course(C1, N1), 
%     scheduled_section_course(C2, N2), N1 != N2, C1!= C2, 
%     overlapping_days(D1, D2), 
%     overlapping_times(S1, E1, S2, E2).


scheduled_conflict(N1, N2) :- 
    scheduled_section_day(N1, D),
    scheduled_section_day(N2, D),
    scheduled_section_course(C1, N1), 
    scheduled_section_course(C2, N2), 
    C1!= C2, N1 != N2,
    scheduled_section_time(N1, S1, E1),
    scheduled_section_time(N2, S2, E2),
    overlapping_times(S1, E1, S2, E2).

scheduled_conflict(N1, N2) :- 
    scheduled_section_time_slot(N1, S1, E1, D1), 
    non_cs_section_time(N2, S2, E2, D2), 
    scheduled_section_course(C1, N1), 
    non_cs_section_course(C2, N2), 
    N1 != N2, C1!= C2, 
    overlapping_days(D1, D2), 
    overlapping_times(S1, E1, S2, E2).
>>>>>>> d79988f528f918b455e0fddb541282e8fb355a1b:clingo/overlap_minimizer_rewrite_jorge.lp

% scheduled_conflict(C1, C2, S1, E1, S2, E2, D1, D2) :- scheduled_section(C1, _, _, S1, E1, D1, _, _), scheduled_section(C2, _, _, S2, E2, D2, _, _), C1!=C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2).
% Additionally, there is conflict between CS sections and non-CS sections. 
% scheduled_conflict(C1, C2, S1, E1, S2, E2, D1, D2) :- scheduled_section(C1, _, _, S1, E1, D1, _, _), non_cs_section(C2, S2, E2, D2), C1!=C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2). 

% There exists at least some non_ovlerapping_courses between C1 and C2.
% Non-conflicting classes, C1 and C2
non_ovlerapping_courses(C1, C2) :- scheduled_section_course(C1, N1), scheduled_section_course(C2, N2), not scheduled_conflict(N1, N2), C1!=C2.
non_ovlerapping_courses(C1, C2) :- scheduled_section_course(C1, N1), non_cs_section_course(C2, N2), not scheduled_conflict(N1, N2), C1!=C2.
% non_ovlerapping_courses(C1, C2) :- scheduled_section(C1, _, _, S1, E1, D1, _, _), non_cs_section(C2, S2, E2, D2), not scheduled_conflict(C1, C2, S1, E1, S2, E2, D1, D2), C1!=C2.

% There are no non_ovlerapping_coursess between C1 and C2 -> total overlap.
% Overlap if all sections are in conflict
scheduled_overlapping_courses(C1, C2) :- class(C1), class(C2), not non_ovlerapping_courses(C1, C2), C1!=C2.
scheduled_overlapping_courses(C1, C2) :- class(C1), non_cs_class(C2), not non_ovlerapping_courses(C1, C2), C1!=C2.
% scheduled_overlapping_courses(C1, C2) :- class(C1), non_cs_class(C2), not non_ovlerapping_courses(C1, C2), C1!=C2.
% Overlap between cs and non-cs classes are not bidirectional,
% while overlap between two cs classes is bidirectional
% enforcing bidirectionality keeps weights the same
% TODO: look into whether or not it is better to enforce
% non-directed overlap
scheduled_overlapping_courses(C1, C2) :- scheduled_overlapping_courses(C2, C1).

true_scheduled_overlapping_courses(C1, C2) :- scheduled_overlapping_courses(C1, C2), not true_scheduled_overlapping_courses(C2, C1).

% calculate the weight for each overlap
scheduled_weighted_overlap_sum(C1, C2, W1 + W2) :- true_scheduled_overlapping_courses(C1, C2), planned_course(C1, W1, Y1), planned_course(C2, W2, Y2).

% scheduled_conflict(C1, C2) :- scheduled_conflict(C1, C2, _, _, _, _, _, _).
% scheduled_weighted_conflict(C1, C2, W1 + W2) :- scheduled_conflict(C1, C2), planned_course(C1, W1, Y1), planned_course(C2, W2, Y2).
% scheduled_overlapping_courses_count(N) :- N = #count{ C1, C2 : scheduled_overlapping_courses(C1, C2) }.
% scheduled_conflict_count(N) :- N = #count{ C1, C2 : scheduled_conflict(C1, C2) }.

<<<<<<< HEAD:clingo/overlap_minimizer_rewrite.lp
% #show scheduled_section/8.
=======
% #show scheduled_section_time_slot/4.
#show scheduled_section/8.
>>>>>>> d79988f528f918b455e0fddb541282e8fb355a1b:clingo/overlap_minimizer_rewrite_jorge.lp

% It cannot be that we generate a new schedule that has more overlap than the original schedule.
% :- original_weighted_overlap_sum(N1), scheduled_weighted_overlap_sum(N2), N2>=N1.
:- original_weighted_overlap_sum(N1), N1 <= #sum{ W, C1, C2 : scheduled_weighted_overlap_sum(C1, C2, W) }.

% There is a shedule change between two section IDs if they are at different times or different days.
<<<<<<< HEAD:clingo/overlap_minimizer_rewrite.lp
% schedule_change(C, I) :- scheduled_section(C, I, N, S1, E1, D1, R, P), section(C, I, N, S2, E2, D2, R, P), S1 != S2, E1 != E2. 
% schedule_change(C, I) :- scheduled_section(C, I, N, S1, E1, D1, R, P), section(C, I, N, S2, E2, D2, R, P), D1 != D2. 
=======
>>>>>>> d79988f528f918b455e0fddb541282e8fb355a1b:clingo/overlap_minimizer_rewrite_jorge.lp
schedule_change(C, I) :- scheduled_section_time_slot(N, S1, E1, D1), section(C, I, N, S2, E2, D2, R, P), S1 != S2, E1 != E2. 
schedule_change(C, I) :- scheduled_section_time_slot(N, S1, E1, D1), section(C, I, N, S2, E2, D2, R, P), D1 != D2. 

% #minimize{W, C1, C2 : scheduled_weighted_overlap_sum(C1, C2, W)}.

% Prioritized minimize functions, try to minimize overlaps, then minimize individual conflicts. 
% TODO: look into how long this takes
#minimize{W@2, C1, C2 : scheduled_weighted_overlap_sum(C1, C2, W)}.
% TODO: should we minimize this based on weight or count them all the same?
#minimize{1@1, C, I : schedule_change(C, I)}.
% #minimize{scheduled_weighted_overlap_sum}.