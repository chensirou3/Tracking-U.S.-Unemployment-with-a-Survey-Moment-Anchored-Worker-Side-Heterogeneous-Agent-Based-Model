"""
Module B: Scheduler / Simulation Clock
Main simulation loop that executes all blocks in fixed monthly order.
"""
import numpy as np
import time
from Phase3_Code.constants import *
from Phase3_Code.environment import Environment
from Phase3_Code.labor.participation import participation_block
from Phase3_Code.labor.search import search_block
from Phase3_Code.labor.opportunity import opportunity_block
from Phase3_Code.labor.acceptance import acceptance_block
from Phase3_Code.household.consumption import consumption_block
from Phase3_Code.household.borrowing import borrowing_block
from Phase3_Code.state_update import (update_labor_states, update_income,
                                       update_expectations)
from Phase3_Code.aggregator import compute_aggregates
from Phase3_Code.mechanism_config import default_config


class Simulation:
    """
    Main simulation engine.

    Monthly execution order:
    1. Read environment
    2. Update expectations (fast states)
    3. Participation block
    4. Search block
    5. Opportunity block
    6. Acceptance block
    7. Apply labor transitions
    8. Update income
    9. Consumption block
    10. Borrowing/liquidity block
    11. Aggregate and record
    """

    def __init__(self, population_path='Phase2_Output/population_v1.npz',
                 T=120, scenario='baseline', seed=42, config=None,
                 env_override=None):
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.config = config if config is not None else default_config()

        # Load population
        pop = np.load(population_path)
        self.st = pop['static_traits'].copy()
        self.cs = pop['category_states'].copy()
        self.ds = pop['dynamic_states'].copy()
        self.bp = pop['behavior_params'].copy()
        self.N = self.st.shape[0]

        # Environment: allow external override (e.g. RealEnvironment)
        if env_override is not None:
            self.env = env_override
            self.T = env_override.T
        else:
            self.env = Environment(T=T, scenario=scenario, seed=seed + 1000)
            self.T = T

        # History
        self.history = []

        # Previous income for consumption block
        self.prev_income = self.ds[:, DS_HH_INCOME].copy()

    def run(self, verbose=True):
        """Run simulation for T months."""
        t0 = time.time()

        cfg = self.config
        for t in range(self.T):
            env = self.env.get(t)

            # --- Step 2: Update expectations ---
            update_expectations(self.cs, self.ds, env, self.rng, cfg)

            # --- Step 3: Participation block ---
            exit_to_n, enter_from_n = participation_block(
                self.cs, self.ds, self.st, env, self.rng, cfg)

            # --- Step 4: Search block ---
            new_search = search_block(
                self.cs, self.ds, self.bp, env, self.rng, cfg)
            self.ds[:, DS_SEARCH_INT] = new_search

            # --- Step 5: Opportunity block ---
            has_offer, offered_wage, is_separated = opportunity_block(
                self.cs, self.ds, self.bp, env, self.rng, cfg)

            # --- Step 6: Acceptance block ---
            accepts = acceptance_block(
                self.cs, self.ds, self.bp, has_offer, offered_wage,
                self.rng, cfg)

            # --- Step 7: Apply labor transitions ---
            transitions = update_labor_states(
                self.cs, self.ds, self.bp,
                exit_to_n, enter_from_n, is_separated, accepts,
                env, self.rng)

            # --- Step 8: Update income ---
            update_income(self.cs, self.ds, self.st, env, self.rng)

            # --- Step 9: Consumption block ---
            consumption, savings = consumption_block(
                self.cs, self.ds, self.bp, env, self.prev_income,
                self.rng, cfg)
            self.prev_income = self.ds[:, DS_HH_INCOME].copy()

            # --- Step 10: Borrowing/liquidity block ---
            new_buf, new_liq, new_debt = borrowing_block(
                self.cs, self.ds, savings, env, self.rng, cfg)
            self.ds[:, DS_CASH_BUFFER] = new_buf
            self.cs[:, CS_LIQUIDITY_TYPE] = new_liq
            self.ds[:, DS_DEBT_STRESS] = new_debt

            # --- Step 11: Aggregate ---
            agg = compute_aggregates(self.cs, self.ds, self.bp, transitions)
            agg['t'] = t
            self.history.append(agg)

            if verbose and (t % 12 == 0 or t == self.T - 1):
                print(f"  t={t:3d}: UR={agg['unemployment_rate']:.4f} "
                      f"LFPR={agg['lfpr']:.4f} EPOP={agg['epop']:.4f} "
                      f"E={agg['n_employed']} U={agg['n_unemployed']} "
                      f"N={agg['n_nilf']}")

        elapsed = time.time() - t0
        if verbose:
            print(f"\nSimulation complete: {self.T} months, "
                  f"{self.N} agents, {elapsed:.1f}s")
        return self.history
