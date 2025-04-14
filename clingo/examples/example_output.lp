% original_weighted_overlap_sum(6) 
scheduled_section(cist3110,s001,c15462,900,975,mw,
                  peter_kiewit_institute_153,hollie_rosser). 
scheduled_section(cist3110,s002,c15462,900,975,tr,
                  peter_kiewit_institute_153,hollie_rosser). 
scheduled_section(cist1600,s001,c16496,630,705,mw,
                  peter_kiewit_institute_361,derek_babb). 
scheduled_section(csci1200,s002,c14597,900,975,tr,
                  peter_kiewit_institute_276,ash_p_ashokan). 
scheduled_section(csci8456,s001,c18572,810,885,tr,
                  peter_kiewit_institute_153,jorge_fandinno_garcia). 
scheduled_section(csci8456,s002,c18572,810,885,mw,
                  peter_kiewit_institute_153,jorge_fandinno_garcia).
% Optimization: 0 1
% OPTIMUM FOUND

class(cist3110; cist1600; csci1200; csci8456).
room(peter_kiewit_institute_153; peter_kiewit_institute_276; peter_kiewit_institute_361).
professor(hollie_rosser, derek_babb, ash_p_ashokan, jorge_fandinno_garcia).
time_slot(810, 885, tr).
time_slot(810, 885, mw).
time_slot(700, 775, mw).
time_slot(630, 705, mw).
time_slot(900, 975, mw).
time_slot(900, 975, tr).
