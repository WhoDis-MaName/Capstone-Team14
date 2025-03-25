day(m).
day(mw).
day(mwrf).
day(t).
day(tr).
day(w).
day(r).
day(f).

% Direct overlaps
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
overlapping_days(D1, D2) :- 
    day(D1), day(D2), D1 = D2. % Exact match

overlapping_days(D1, D2) :- overlapping_days(D2, D1). % Ensure all overlaps are bidirectional