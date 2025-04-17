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

% Direct overlaps
overlapping_days(mf, m).
overlapping_days(mf, f).
overlapping_days(mw, m).
overlapping_days(mw, w).
overlapping_days(tr, t).
overlapping_days(tr, r).
overlapping_days(mtwr, mw).
overlapping_days(mtwr, tr).
overlapping_days(mtwr, m).
overlapping_days(mtwr, t).
overlapping_days(mtwr, w).
overlapping_days(mtwr, r).
overlapping_days(mwf, m).
overlapping_days(mwf, w).
overlapping_days(mwf, f).
overlapping_days(mwf, mw).
overlapping_days(mwf, mf).
overlapping_days(mwf, mtwr).
overlapping_days(mr, m).
overlapping_days(mr, r).
overlapping_days(mr, mw).
overlapping_days(mr, tr).
overlapping_days(mr, mtwr).
overlapping_days(mr, mwf).
overlapping_days(D1, D2) :- 
    day(D1), day(D2), D1 = D2. % Exact match

overlapping_days(D1, D2) :- overlapping_days(D2, D1). % Ensure all overlaps are bidirectional