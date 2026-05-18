"""
Build real environment from FRED data. Parses inline CSV, aligns, transforms,
and saves to Phase3_Output/real_environment.npz.
"""
import numpy as np, os

os.makedirs('Phase3_Output', exist_ok=True)

def parse(text):
    d, v = [], []
    for ln in text.strip().split('\n'):
        if ',' not in ln or 'date' in ln.lower(): continue
        p = ln.split(',')
        val = p[1].strip()
        if val in ('', '.'): continue
        d.append(p[0].strip()[:7])
        v.append(float(val))
    return dict(zip(d, v))

# Load from data files
import pathlib
data_dir = pathlib.Path('Phase3_Code/fred_data')

with open(data_dir / 'JTSJOR.csv') as f: jtsjor = parse(f.read())
with open(data_dir / 'JTSTSR.csv') as f: jtstsr = parse(f.read())
with open(data_dir / 'UNRATE.csv') as f: unrate = parse(f.read())
with open(data_dir / 'FEDFUNDS.csv') as f: fedfunds = parse(f.read())
with open(data_dir / 'AHETPI.csv') as f: ahetpi = parse(f.read())

# Common dates
common = sorted(set(jtsjor) & set(jtstsr) & set(unrate) & set(fedfunds) & set(ahetpi))
T = len(common)
print(f"Common range: {common[0]} to {common[-1]}, T={T} months")

# Align
a_jtsjor = np.array([jtsjor[d] for d in common])
a_jtstsr = np.array([jtstsr[d] for d in common])
a_unrate = np.array([unrate[d] for d in common])
a_fedfunds = np.array([fedfunds[d] for d in common])
a_ahetpi = np.array([ahetpi[d] for d in common])

# Transform
vu_ratio = a_jtsjor / np.maximum(a_unrate, 0.1)
vu_mean = np.mean(vu_ratio)
market_tightness = vu_ratio / vu_mean

separation_rate = a_jtstsr / 100.0

ahe_growth = np.diff(a_ahetpi) / a_ahetpi[:-1]
income_growth_bg = np.concatenate([[ahe_growth[0]], ahe_growth])

borrowing_rate = a_fedfunds / 100.0
actual_ur = a_unrate / 100.0

np.savez_compressed('Phase3_Output/real_environment.npz',
    dates=np.array(common),
    market_tightness=market_tightness,
    separation_rate=separation_rate,
    income_growth_bg=income_growth_bg,
    borrowing_rate=borrowing_rate,
    actual_ur=actual_ur)

print(f"Saved: T={T}")
print(f"  market_tightness: mean={market_tightness.mean():.3f}, min={market_tightness.min():.3f}, max={market_tightness.max():.3f}")
print(f"  separation_rate:  mean={separation_rate.mean():.4f}, range=[{separation_rate.min():.4f}, {separation_rate.max():.4f}]")
print(f"  income_growth_bg: mean={income_growth_bg.mean():.5f}, std={income_growth_bg.std():.5f}")
print(f"  borrowing_rate:   mean={borrowing_rate.mean():.4f}")
print(f"  actual_ur:        mean={actual_ur.mean():.4f}, range=[{actual_ur.min():.4f}, {actual_ur.max():.4f}]")
