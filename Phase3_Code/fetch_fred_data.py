"""
Fetch FRED data and build real environment paths.
Saves to Phase3_Output/real_environment.npz
"""
import urllib.request
import numpy as np
import os

os.makedirs('Phase3_Output', exist_ok=True)

SERIES = {
    'JTSJOR': 'JOLTS Job Openings Rate (%)',
    'JTSTSR': 'JOLTS Total Separations Rate (%)',
    'UNRATE': 'Unemployment Rate (%)',
    'FEDFUNDS': 'Federal Funds Rate (%)',
    'CES0500000003': 'Avg Hourly Earnings ($)',
}

START = '2001-01-01'
END = '2026-03-31'

def fetch_fred(series_id):
    url = (f"https://fred.stlouisfed.org/graph/fredgraph.csv?"
           f"id={series_id}&cosd={START}&coed={END}&fq=Monthly&fam=avg")
    print(f"  Fetching {series_id}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=30)
    text = resp.read().decode('utf-8')
    dates, vals = [], []
    for line in text.strip().split('\n'):
        if 'date' in line.lower() or ',' not in line:
            continue
        parts = line.split(',')
        d, v = parts[0].strip(), parts[1].strip()
        if v == '' or v == '.':
            continue
        dates.append(d[:7])  # YYYY-MM
        vals.append(float(v))
    return dates, np.array(vals)

print("Downloading FRED data...")
data = {}
for sid in SERIES:
    dates, vals = fetch_fred(sid)
    data[sid] = {'dates': dates, 'values': vals}
    print(f"    {sid}: {len(vals)} obs, {dates[0]} to {dates[-1]}")

# Align all series to common date range
all_dates = set(data['JTSJOR']['dates'])
for sid in SERIES:
    all_dates &= set(data[sid]['dates'])
common_dates = sorted(all_dates)
T = len(common_dates)
print(f"\nCommon range: {common_dates[0]} to {common_dates[-1]}, T={T} months")

# Build aligned arrays
aligned = {}
for sid in SERIES:
    d2v = dict(zip(data[sid]['dates'], data[sid]['values']))
    aligned[sid] = np.array([d2v[d] for d in common_dates])

# === Transform to model environment variables ===

# 1. market_tightness: V/U ratio (openings rate / unemployment rate)
#    Normalize so that historical average ≈ 1.0
vu_ratio = aligned['JTSJOR'] / np.maximum(aligned['UNRATE'], 0.1)
vu_mean = np.mean(vu_ratio)
market_tightness = vu_ratio / vu_mean  # normalized to mean=1

# 2. separation_rate: JTSTSR is total separations as % of employment (monthly)
separation_rate = aligned['JTSTSR'] / 100.0  # convert % to decimal

# 3. income_growth_bg: month-over-month change in avg hourly earnings
ahe = aligned['CES0500000003']
income_growth = np.diff(ahe) / ahe[:-1]  # MoM growth rate
income_growth = np.concatenate([[income_growth[0]], income_growth])  # pad first month

# 4. borrowing_rate: federal funds rate (annual, convert to decimal)
borrowing_rate = aligned['FEDFUNDS'] / 100.0

# Actual unemployment rate for validation
actual_ur = aligned['UNRATE'] / 100.0

# Save
np.savez_compressed('Phase3_Output/real_environment.npz',
    dates=np.array(common_dates),
    market_tightness=market_tightness,
    separation_rate=separation_rate,
    income_growth_bg=income_growth,
    borrowing_rate=borrowing_rate,
    actual_ur=actual_ur,
    jtsjor=aligned['JTSJOR'],
    unrate=aligned['UNRATE'],
)

print(f"\nSaved to Phase3_Output/real_environment.npz")
print(f"  market_tightness: mean={market_tightness.mean():.3f}, "
      f"min={market_tightness.min():.3f}, max={market_tightness.max():.3f}")
print(f"  separation_rate: mean={separation_rate.mean():.4f}, "
      f"min={separation_rate.min():.4f}, max={separation_rate.max():.4f}")
print(f"  income_growth_bg: mean={income_growth.mean():.5f}, "
      f"std={income_growth.std():.5f}")
print(f"  borrowing_rate: mean={borrowing_rate.mean():.4f}")
print(f"  actual_ur: mean={actual_ur.mean():.4f}")
