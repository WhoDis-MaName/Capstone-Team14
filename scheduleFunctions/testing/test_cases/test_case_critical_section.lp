% Course weight: (course name, weight, year)
course_weight(cist1400, 1, 1).
course_weight(cist1500, 1, 1).

section(cist1400, s001, c10001, 900, 975, mw, room1, prof1).
critical_section(cist1400, c10001).

section(cist1500, s001, c10002, 900, 975, mw, room2, prof2).
critical_section(cist1500, c10002).

class(cist1400; cist1500).
room(room1; room2).
professor(prof1, prof2).
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
