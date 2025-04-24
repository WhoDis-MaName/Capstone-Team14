day(m).
day(mw).
day(mwf).
day(mwrf).
day(t).
day(tr).
day(w).
day(r).
day(f).
day(mf).
day(mr).

day_slot(mf, m).
day_slot(mf, f).
day_slot(mw, m).
day_slot(mw, w).
day_slot(tr, t).
day_slot(tr, r).
day_slot(mtwr, m).
day_slot(mtwr, t).
day_slot(mtwr, w).
day_slot(mtwr, r).
day_slot(mwf, m).
day_slot(mwf, w).
day_slot(mwf, f).
day_slot(mr, m).
day_slot(mr, r).
day_slot(mr, tr).

overlapping_days(DS1, DS2) :- day_slot(DS1, D), day_slot(DS2, D). % Overlapping days
overlapping_days(D, D) :- day(D).

% Direct overlaps
% overlapping_days(mf, m).
% overlapping_days(mf, f).
% overlapping_days(mw, m).
% overlapping_days(mw, w).
% overlapping_days(tr, t).
% overlapping_days(tr, r).
% overlapping_days(mtwr, mw).
% overlapping_days(mtwr, tr).
% overlapping_days(mtwr, m).
% overlapping_days(mtwr, t).
% overlapping_days(mtwr, w).
% overlapping_days(mtwr, r).
% overlapping_days(mwf, m).
% overlapping_days(mwf, w).
% overlapping_days(mwf, f).
% overlapping_days(mwf, mw).
% overlapping_days(mwf, mf).
% overlapping_days(mwf, mtwr).
% overlapping_days(mr, m).
% overlapping_days(mr, r).
% overlapping_days(mr, mw).
% overlapping_days(mr, tr).
% overlapping_days(mr, mtwr).
% overlapping_days(mr, mwf).
% overlapping_days(D1, D2) :- 
%     day(D1), day(D2), D1 = D2. % Exact match

overlapping_days(D1, D2) :- overlapping_days(D2, D1). % Ensure all overlaps are bidirectional