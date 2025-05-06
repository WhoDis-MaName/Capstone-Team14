course_year(csci4150, 4).
section(csci4150, s001, c15236, 
        900, 975, mw, room3, prof3).
course_year(csci4220, 4).
section(csci4220, s001, c16070, 
        960, 1035, mw, room4, prof4).
course_year(cist2100, 2).
section(cist2100, s001, c20001, 
        900, 975, mw, room1, prof1).
course_year(cist2500, 2).
section(cist2500, s001, c20003, 
        900, 975, mw, room2, prof2).

class(cist2100; cist2500; csci4220; csci4150).
time_slot_credits(960, 1035, mw, 3).
time_slot_credits(900, 975, mw, 3).  
time_slot_credits(900, 975, tr, 3).  

mw_preference(prof3).