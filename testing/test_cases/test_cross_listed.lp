course_weight(cist2100, 2, 2).
course_weight(cist2200, 3, 2).

section(csci4150, s001, c15236, 900, 975, mw, room3, hesham_hassan_ali).
critical_section(csci4150, c15236).
course(csci4150, "graph_theory", "_").
course_weight(csci4150, 1, 4).

section(csci8156, s001, c15237, 900, 975, mw, room3, hesham_hassan_ali).
critical_section(csci8156, c15237).
course_weight(csci8156, 1, 4).
course(csci8156, "graph_theory", "_").

course(csci4220, "princ_of_programming_languages", "_").
course_weight(csci4220, 1, 4).
section(csci4220, s001, c16070, 960, 1035, mw, room4, fabio_torres_vitor).
critical_section(csci4220, c16070).

section(cist2100, s001, c20001, 900, 975, mw, room1, prof1).
critical_section(cist2100, c20001).

section(cist2200, s001, c20003, 900, 975, mw, room2, prof2).
critical_section(cist2200, c20003).

class(cist2100; cist2200).
room(room1; room2; room3; room4).
professor(prof1, prof2; hesham_hassan_ali; fabio_torres_vitor).
time_slot(900, 975, mw).
time_slot(900, 975, tr).
time_slot(720, 795, f).
time_slot(780, 855, mw).
time_slot(570, 620, m).
time_slot(900, 975, tr).
time_slot(630, 705, mw).
time_slot(810, 885, tr).
time_slot(570, 620, t).
time_slot(900, 975, mw).
time_slot(960, 1035, mw).
