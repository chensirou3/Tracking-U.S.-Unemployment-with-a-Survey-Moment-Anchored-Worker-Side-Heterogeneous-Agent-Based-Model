"""Audit which CSV months are present vs the 2001-01..2026-02 expected calendar."""
import csv

exp = set()
y, m = 2001, 1
while (y, m) <= (2026, 2):
    exp.add(f'{y:04d}-{m:02d}')
    m += 1
    if m > 12:
        m = 1; y += 1
print(f'Expected months 2001-01 .. 2026-02: {len(exp)}')

for fname in ['UNRATE.csv', 'CIVPART.csv', 'EMRATIO.csv', 'JTSJOR.csv', 'JTSLDR.csv',
              'FEDFUNDS.csv', 'CES0500000003.csv']:
    g = set()
    with open(f'Phase3_Data/{fname}') as f:
        r = csv.reader(f); next(r)
        for row in r:
            g.add(row[0][:7])
    miss = sorted(exp - g)
    extra = sorted(g - exp)
    msg_miss = miss[:5]
    msg_ex = extra[:5]
    print(f'{fname:22s}: present={len(g):3d}  missing_in_calendar={len(miss):3d} {msg_miss}  '
          f'extra_outside_calendar={len(extra):3d} {msg_ex}')
