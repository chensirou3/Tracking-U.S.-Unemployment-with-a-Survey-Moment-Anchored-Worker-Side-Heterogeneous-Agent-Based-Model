"""Download FRED data to local CSV files."""
import urllib.request, os, time, ssl

os.makedirs('Phase3_Code/fred_data', exist_ok=True)

# Bypass SSL issues
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

series = ['JTSJOR', 'JTSTSR', 'UNRATE', 'FEDFUNDS', 'AHETPI']

for sid in series:
    url = (f"https://fred.stlouisfed.org/graph/fredgraph.csv?"
           f"id={sid}&cosd=2001-01-01&coed=2026-03-31&fq=Monthly&fam=avg")
    out = f'Phase3_Code/fred_data/{sid}.csv'
    print(f"Downloading {sid}...", end=' ')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=30, context=ctx)
        data = resp.read().decode('utf-8')
        with open(out, 'w') as f:
            f.write(data)
        lines = len([l for l in data.strip().split('\n') if ',' in l and 'date' not in l.lower()])
        print(f"OK ({lines} obs)")
    except Exception as e:
        print(f"FAILED: {e}")
    time.sleep(1)

print("Done.")
