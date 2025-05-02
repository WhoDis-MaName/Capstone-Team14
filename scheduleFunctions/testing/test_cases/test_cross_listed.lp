course_weight(cist2100, 2, 2).
course_weight(cist2200, 3, 2).

section(csci4150, s001, c15236, 900, 975, mw, room3, hesham_hassan_ali).

course(csci4150, "graph_theory", "_").
course_weight(csci4150, 1, 4).

section(csci8156, s001, c15237, 900, 975, mw, room3, hesham_hassan_ali).

course_weight(csci8156, 1, 4).
course(csci8156, "graph_theory", "_").

course(csci4220, "princ_of_programming_languages", "_").
course_weight(csci4220, 1, 4).
section(csci4220, s001, c16070, 960, 1035, mw, room4, fabio_torres_vitor).


section(cist2100, s001, c20001, 900, 975, mw, room1, prof1).

section(cist2200, s001, c20003, 900, 975, mw, room2, prof2).


class(cist2100; cist2200).
room(room1; room2; room3; room4).
professor(prof1, prof2; hesham_hassan_ali; fabio_torres_vitor).
time_slot_credits(900, 975, mw, 3).
time_slot_credits(900, 975, tr, 3).
time_slot_credits(720, 795, f, 1).
time_slot_credits(780, 855, mw, 5).
time_slot_credits(570, 620, m, 4).
time_slot_credits(900, 975, tr, 2).
time_slot_credits(630, 705, mw, 7).
time_slot_credits(810, 885, tr, 8).
time_slot_credits(570, 620, t, 3).
time_slot_credits(960, 1035, mw, 5).
