"""
Real historical environment from FRED data.
Period: 2001-01 to 2026-02 (302 months)

Maps FRED series to model environment variables:
- JTSJOR (Job Openings Rate) -> market_tightness (normalized: rate/3.0)
- JTSLDR (Layoffs/Discharges Rate) -> separation_rate (rate/100)
- CES0500000003_PC1 (Earnings YoY) -> income_growth_bg (rate/100/12)
- FEDFUNDS -> borrowing_rate (rate/100 + 0.02 spread)
"""
import numpy as np
import csv
import os


class RealEnvironment:
    def __init__(self, data_dir='Phase3_Data', start='2001-01', end='2026-02'):
        self.start = start
        self.end = end
        self._load_data(data_dir)

    def _load_csv(self, path):
        data = {}
        with open(path, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                date_str = row[0][:7]
                try:
                    val = float(row[1])
                    data[date_str] = val
                except (ValueError, IndexError):
                    pass
        return data

    def _load_data(self, data_dir):
        jtsjor = self._load_csv(os.path.join(data_dir, 'JTSJOR.csv'))
        jtsldr = self._load_csv(os.path.join(data_dir, 'JTSLDR.csv'))
        fedfunds = self._load_csv(os.path.join(data_dir, 'FEDFUNDS.csv'))
        earnings = self._load_csv(os.path.join(data_dir, 'CES0500000003.csv'))

        self.dates = []
        y, m = int(self.start[:4]), int(self.start[5:7])
        ey, em = int(self.end[:4]), int(self.end[5:7])
        while (y, m) <= (ey, em):
            self.dates.append(f'{y:04d}-{m:02d}')
            m += 1
            if m > 12:
                m = 1
                y += 1

        self.T = len(self.dates)
        self.market_tightness = np.zeros(self.T)
        self.separation_rate = np.zeros(self.T)
        self.income_growth_bg = np.zeros(self.T)
        self.borrowing_rate = np.zeros(self.T)

        for i, d in enumerate(self.dates):
            jor = jtsjor.get(d, 3.0)
            self.market_tightness[i] = jor / 3.0

            ldr = jtsldr.get(d, 1.2)
            self.separation_rate[i] = ldr / 100.0

            earn = earnings.get(d, 3.0)
            self.income_growth_bg[i] = earn / 100.0 / 12.0

            ff = fedfunds.get(d, 2.0)
            self.borrowing_rate[i] = (ff + 2.0) / 100.0

        self.market_tightness = np.clip(self.market_tightness, 0.3, 3.0)
        self.separation_rate = np.clip(self.separation_rate, 0.005, 0.05)
        self.income_growth_bg = np.clip(self.income_growth_bg, -0.01, 0.02)
        self.borrowing_rate = np.clip(self.borrowing_rate, 0.02, 0.15)

    def get(self, t):
        t = min(t, self.T - 1)
        return {
            'market_tightness': self.market_tightness[t],
            'separation_rate': self.separation_rate[t],
            'income_growth_bg': self.income_growth_bg[t],
            'borrowing_rate': self.borrowing_rate[t],
        }

    def summary(self):
        print(f"Real Environment: {self.dates[0]} to {self.dates[-1]} ({self.T} months)")
        for name in ['market_tightness', 'separation_rate',
                      'income_growth_bg', 'borrowing_rate']:
            arr = getattr(self, name)
            print(f"  {name}: mean={arr.mean():.4f}, "
                  f"min={arr.min():.4f}, max={arr.max():.4f}")
