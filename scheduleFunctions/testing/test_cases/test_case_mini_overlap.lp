% Course weight: (course name, weight, year)
course_weight(cist3110, 1, 3).

% section: (course name, section number, section ID, start time, end time, dayslot, room, professor)
section(cist3110, s001, c15462, 900, 975, mw, 
        peter_kiewit_institute_153, hollie_rosser).

% We say that each course has a critical section assigned to section 001's unique id. 
critical_section(cist3110, c15462).
section(cist3110, s002, c15463, 900, 975, tr, 
        peter_kiewit_institute_153, hollie_rosser).

course_weight(cist1600, 1, 1).
section(cist1600, s001, c16496, 630, 705, mw, 
        peter_kiewit_institute_361, derek_babb).
critical_section(cist1600, c16496).

course_weight(csci1200, 1, 1).
section(csci1200, s002, c14597, 700, 775, mw, 
        peter_kiewit_institute_276, ash_p_ashokan).

course_weight(csci8456, 1, 5).
section(csci8456, s001, c18572, 700, 775, mw, 
        peter_kiewit_institute_153, jorge_fandinno_garcia).
critical_section(csci8456, c18572).
section(csci8456, s002, c18573, 810, 885, mw, 
        peter_kiewit_institute_153, jorge_fandinno_garcia).
        
class(cist3110; cist1600; csci1200; csci8456).
room(peter_kiewit_institute_153; peter_kiewit_institute_276; peter_kiewit_institute_361).
professor(hollie_rosser, derek_babb, ash_p_ashokan, jorge_fandinno_garcia).
time_slot(810, 885, tr).
time_slot(810, 885, mw).
time_slot(700, 775, mw).
time_slot(630, 705, mw).
time_slot(900, 975, mw).
time_slot(900, 975, tr).
