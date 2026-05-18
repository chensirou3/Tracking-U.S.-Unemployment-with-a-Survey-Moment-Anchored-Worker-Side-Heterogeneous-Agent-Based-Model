"""
Module A: Environment Module
Defines exogenous environment paths for each simulation month.
"""
import numpy as np


class Environment:
    """
    Exogenous environment that drives agent decisions each month.

    All paths are arrays of length T (number of months).
    """

    def __init__(self, T=120, scenario='baseline', seed=42):
        self.T = T
        self.scenario = scenario
        self.rng = np.random.default_rng(seed)
        self._build_paths()

    def _build_paths(self):
        T = self.T
        t = np.arange(T)

        if self.scenario == 'baseline':
            # Stable economy with mild fluctuations
            self.market_tightness = 1.0 + 0.05 * np.sin(2 * np.pi * t / 60)
            self.separation_rate = 0.012 + 0.002 * np.sin(2 * np.pi * t / 60 + np.pi)
            self.income_growth_bg = 0.002 + 0.001 * np.sin(2 * np.pi * t / 60)
            self.borrowing_rate = 0.05 * np.ones(T)

        elif self.scenario == 'recession':
            # Stable for 36 months, recession at 36-48, slow recovery after
            self.market_tightness = np.ones(T)
            self.separation_rate = 0.012 * np.ones(T)
            self.income_growth_bg = 0.002 * np.ones(T)
            self.borrowing_rate = 0.05 * np.ones(T)

            # Recession shock at t=36
            recession = np.zeros(T)
            for i in range(T):
                if 36 <= i < 48:
                    recession[i] = (i - 36) / 12  # ramp up
                elif 48 <= i < 60:
                    recession[i] = 1.0  # peak
                elif 60 <= i < 84:
                    recession[i] = max(0, 1.0 - (i - 60) / 24)  # slow recovery

            self.market_tightness -= 0.4 * recession
            self.separation_rate += 0.015 * recession
            self.income_growth_bg -= 0.005 * recession
            self.borrowing_rate += 0.03 * recession

        elif self.scenario == 'constant':
            # Flat environment for testing
            self.market_tightness = np.ones(T)
            self.separation_rate = 0.012 * np.ones(T)
            self.income_growth_bg = 0.002 * np.ones(T)
            self.borrowing_rate = 0.05 * np.ones(T)

        else:
            raise ValueError(f"Unknown scenario: {self.scenario}")

        # Clip to reasonable ranges
        self.market_tightness = np.clip(self.market_tightness, 0.3, 2.0)
        self.separation_rate = np.clip(self.separation_rate, 0.005, 0.05)
        self.income_growth_bg = np.clip(self.income_growth_bg, -0.01, 0.01)
        self.borrowing_rate = np.clip(self.borrowing_rate, 0.02, 0.15)

    def get(self, t):
        """Return environment dict for month t."""
        return {
            'market_tightness': self.market_tightness[t],
            'separation_rate': self.separation_rate[t],
            'income_growth_bg': self.income_growth_bg[t],
            'borrowing_rate': self.borrowing_rate[t],
        }
