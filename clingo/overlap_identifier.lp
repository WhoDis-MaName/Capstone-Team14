% #include "total_filtered.lp".
% #include "filtered_test.lp".
% #include "example_output.lp".
% #include "..\\testing\\test_cases\\test_case_mini_overlap.lp".
% #include "..\\testing\\test_cases\\test_case_english.lp".
% #include "..\\testing\\test_cases\\test_case_01.lp".
% #include "..\\testing\\test_cases\\test_case_00.lp".
% #include "output.lp".
% #include "fourYearPlanTest.lp".
#include "fourYearPlan.lp".
#include "days.lp".
#include "overlap.lp".
% #include "groups.lp".

planned_course(C, 1, 0) :- class(C), not planned_classes(C).

% Example course from classes.lp:
% course("CSCI4830", "INTRODUCTN SOFTWARE ENGINEERNG", "-").

% Goal: Show when there is a conflict between two classes
% Day slot and time slots separate
% Time slots have start time and end time in minutes past midnight: ie: (60, 135) = (1:00am, 2:15 am)
% Day possibililtes are: MW, TR, M, T, W, R, F, MTWR
% Times are usually hour long windows, but can be longer if the class only meets once a week

% There is conflict if: 
% - there does not exist at least one section from each module from a group that does not have conflict
conflict(C1, C2, S1, E1, S2, E2, D1, D2) :- section(C1, S1, E1, D1), section(C2, S2, E2, D2), C1!=C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2).

% Additionally, there is conflict between CS sections and non-CS sections. 
conflict(C1, C2, S1, E1, S2, E2, D1, D2) :- section(C1, S1, E1, D1), non_cs_section(C2, S2, E2, D2), C1!=C2, overlapping_days(D1, D2), overlapping_times(S1, E1, S2, E2).

conflict(C1, C2) :- conflict(C1, C2, _, _, _, _, _, _).

% There exists at least some path between C1 and C2.
% non-conflicting classes
path(C1, C2) :- section(C1, S1, E1, D1), section(C2, S2, E2, D2), not conflict(C1, C2, S1, E1, S2, E2, D1, D2), C1!=C2.

% There is also a path between non_cs sections and cs_sections
path(C1, C2) :- section(C1, S1, E1, D1), non_cs_section(C2, S2, E2, D2), not conflict(C1, C2, S1, E1, S2, E2, D1, D2), C1!=C2.

% There are no paths between C1 and C2 -> total overlap.
overlap(C1, C2) :- class(C1), class(C2), not path(C1, C2), C1!=C2.
overlap(C1, C2) :- class(C1), non_cs_class(C2), not path(C1, C2), C1!=C2.
% Overlap between cs and non-cs classes are not bidirectional,
% while overlap between two cs classes is bidirectional
% enforcing bidirectionality keeps weights the same
% TODO: look into whether or not it is better to enforce
% non-directed overlap
overlap(C1, C2) :- overlap(C2, C1).

weighted_overlap(C1, C2, W1 + W2) :- overlap(C1, C2), planned_course(C1, W1, Y1), planned_course(C2, W2, Y2).
original_weighted_overlap_sum(N) :- N = #sum{ W, C1, C2 : weighted_overlap(C1, C2, W) }.

% #show overlap/2.
#show original_weighted_overlap_sum/1.

% overlap_count(N) :- N = #count{ C1 : overlap(C1, C2) }.
% conflict_count(N) :- N = #count{ C1 : conflict(C1, C2) }.
% overlap_count(N) :- N = #count{ C1, C2 : overlap(C1, C2) }.
% conflict_count(N) :- N = #count{ C1, C2 : conflict(C1, C2) }.

% #show overlap_count/1.
% #show conflict_count/1.
% #show overlap/2.
% #show planned_course/3.
% #show conflict/2.
% #show path/2.