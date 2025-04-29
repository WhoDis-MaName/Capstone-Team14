course_weight(cist3100, 1, 3).
course_weight(cist3200, 1, 3).

section(cist3100, s001, c30001, 780, 855, mw, room1, prof1).
critical_section(cist3100, c30001).

section(cist3200, s001, c30002, 780, 855, mw, room2, prof2).
critical_section(cist3200, c30002).
section(cist3200, s002, c30003, 810, 885, mw, room2, prof2).

class(cist3100; cist3200).
room(room1; room2).
professor(prof1, prof2).
time_slot(810, 885, mw).
time_slot(900, 975, mw).
time_slot(720, 795, f).
time_slot(780, 855, mw).
time_slot(570, 620, m).
time_slot(900, 975, tr).
time_slot(630, 705, mw).
time_slot(810, 885, tr).
time_slot(570, 620, t).