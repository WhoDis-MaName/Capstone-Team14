course_year(csci4150, 4).
section(csci4150, s001, c15236, 900, 975, mw, room3, prof3).
course_year(csci8156, 5).
section(csci8156, s001, c15237, 900, 975, mw, room3, prof3).
course_year(csci8157, 5).
section(csci8157, s001, c15238, 900, 975, mw, room5, prof5).
course_year(csci4220, 4).
section(csci4220, s001, c16070, 960, 1035, mw, room4, prof4).
course_year(cist2100, 2).
section(cist2100, s001, c20001, 900, 975, mw, room1, prof1).
course_year(cist2500, 2).
section(cist2500, s001, c20003, 900, 975, mw, room2, prof2).

class(cist2100; cist2500; csci4220; csci4150; csci8156; csci8157).

time_slot_credits(900, 975, mw, 3).  time_slot_credits(720, 795, f, 1).
time_slot_credits(900, 975, tr, 3).  time_slot_credits(780, 855, mw, 5).
time_slot_credits(570, 620, t, 3).   time_slot_credits(570, 620, m, 4).
time_slot_credits(960, 1035, mw, 3). time_slot_credits(900, 975, tr, 2).