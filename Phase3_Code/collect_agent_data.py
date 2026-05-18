"""
Phase 5 - Collect agent-level decision data for behavioral identification.

Strategy: run simulation with logging enabled.
Every `sample_interval` months, snapshot ALL agent states + decisions.
Uses a subsample of agents to keep memory manageable.
"""
import sys, os, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase3_Code.constants import *
from Phase3_Code.environment_real import RealEnvironment
from Phase3_Code.mechanism_config import default_config
from Phase3_Code.labor.participation import participation_block
from Phase3_Code.labor.search import search_block
from Phase3_Code.labor.opportunity import opportunity_block
from Phase3_Code.labor.acceptance import acceptance_block
from Phase3_Code.household.consumption import consumption_block
from Phase3_Code.household.borrowing import borrowing_block
from Phase3_Code.state_update import (update_labor_states, update_income,
                                       update_expectations)


def collect_data(sample_n=10000, sample_interval=1, seed=42):
    """
    Run simulation and collect agent-level decision data.

    Args:
        sample_n: number of agents to track (random subsample)
        sample_interval: record every N months (1 = every month)

    Returns:
        records: dict of arrays, each (n_records,)
    """
    cfg = default_config()
    rng = np.random.default_rng(seed)
    env_obj = RealEnvironment(data_dir='Phase3_Data')
    T = env_obj.T

    # Load population
    pop = np.load('Phase2_Output/population_v1.npz')
    st = pop['static_traits'].copy()
    cs = pop['category_states'].copy()
    ds = pop['dynamic_states'].copy()
    bp = pop['behavior_params'].copy()
    N = st.shape[0]

    # Subsample indices (fixed throughout run)
    idx = rng.choice(N, size=min(sample_n, N), replace=False)
    idx.sort()

    prev_income = ds[:, DS_HH_INCOME].copy()

    # Pre-allocate record lists
    rec = {k: [] for k in [
        't', 'agent_id',
        # Static traits
        'age', 'education', 'marital', 'hh_size',
        # Category states (pre-decision)
        'emp_state', 'liq_type', 'housing', 'con_type',
        # Dynamic states (pre-decision)
        'income_exp', 'income_unc', 'labor_frag', 'cash_buffer',
        'search_int_pre', 'mobility_fric', 'hh_income', 'unemp_dur', 'debt_stress',
        # Behavior params
        'mpc_pos', 'mpc_neg', 'resv_wage', 'flexibility',
        # Environment
        'market_tight', 'sep_rate', 'income_growth', 'borrow_rate',
        # --- DECISIONS / OUTCOMES ---
        'did_exit_lf', 'did_enter_lf',
        'search_int_post',
        'got_offer', 'offered_wage', 'did_accept',
        'was_separated',
        'consumption', 'savings',
        'new_buffer', 'new_liq_type', 'new_debt_stress',
        # Transitions
        'new_emp_state',
    ]}

    print(f"Collecting data: {T} months, {len(idx)} agents/month, interval={sample_interval}")
    t0 = time.time()

    for t in range(T):
        env = env_obj.get(t)

        # Step 2: expectations
        update_expectations(cs, ds, env, rng, cfg)

        # Step 3: participation
        exit_to_n, enter_from_n = participation_block(cs, ds, st, env, rng, cfg)

        # Step 4: search
        new_search = search_block(cs, ds, bp, env, rng, cfg)
        search_pre = ds[:, DS_SEARCH_INT].copy()
        ds[:, DS_SEARCH_INT] = new_search

        # Step 5: opportunity
        has_offer, offered_wage, is_separated = opportunity_block(cs, ds, bp, env, rng, cfg)

        # Step 6: acceptance
        accepts = acceptance_block(cs, ds, bp, has_offer, offered_wage, rng, cfg)

        # Snapshot BEFORE transitions (for recording)
        emp_pre = cs[:, CS_EMPLOYMENT].copy()

        # Step 7: transitions
        transitions = update_labor_states(cs, ds, bp, exit_to_n, enter_from_n,
                                          is_separated, accepts, env, rng)
        # Step 8: income
        update_income(cs, ds, st, env, rng)

        # Step 9: consumption
        consumption, savings = consumption_block(cs, ds, bp, env, prev_income, rng, cfg)
        prev_income = ds[:, DS_HH_INCOME].copy()

        # Step 10: borrowing
        new_buf, new_liq, new_debt = borrowing_block(cs, ds, savings, env, rng, cfg)
        ds[:, DS_CASH_BUFFER] = new_buf
        cs[:, CS_LIQUIDITY_TYPE] = new_liq
        ds[:, DS_DEBT_STRESS] = new_debt

        # Record subsample
        if t % sample_interval == 0:
            n = len(idx)
            rec['t'].append(np.full(n, t, dtype=np.int16))
            rec['agent_id'].append(idx.astype(np.int32))
            # Static
            rec['age'].append(st[idx, ST_AGE])
            rec['education'].append(st[idx, ST_EDUCATION])
            rec['marital'].append(st[idx, ST_MARITAL])
            rec['hh_size'].append(st[idx, ST_HH_SIZE])
            # Category (pre)
            rec['emp_state'].append(emp_pre[idx])
            rec['liq_type'].append(cs[idx, CS_LIQUIDITY_TYPE])  # post-update
            rec['housing'].append(cs[idx, CS_HOUSING_STATUS])
            rec['con_type'].append(cs[idx, CS_CONSUMPTION_TYPE])
            # Dynamic (pre-decision values from this step)
            rec['income_exp'].append(ds[idx, DS_INCOME_EXP])
            rec['income_unc'].append(ds[idx, DS_INCOME_UNC])
            rec['labor_frag'].append(ds[idx, DS_LABOR_FRAG])
            rec['cash_buffer'].append(ds[idx, DS_CASH_BUFFER])
            rec['search_int_pre'].append(search_pre[idx])
            rec['mobility_fric'].append(ds[idx, DS_MOBILITY_FRIC])
            rec['hh_income'].append(ds[idx, DS_HH_INCOME])
            rec['unemp_dur'].append(ds[idx, DS_UNEMP_DUR])
            rec['debt_stress'].append(ds[idx, DS_DEBT_STRESS])

            # Behavior params
            rec['mpc_pos'].append(bp[idx, BP_MPC_POS])
            rec['mpc_neg'].append(bp[idx, BP_MPC_NEG])
            rec['resv_wage'].append(bp[idx, BP_RESV_WAGE])
            rec['flexibility'].append(bp[idx, BP_FLEXIBILITY])
            # Environment
            rec['market_tight'].append(np.full(n, env['market_tightness']))
            rec['sep_rate'].append(np.full(n, env['separation_rate']))
            rec['income_growth'].append(np.full(n, env['income_growth_bg']))
            rec['borrow_rate'].append(np.full(n, env['borrowing_rate']))
            # Decisions
            rec['did_exit_lf'].append(exit_to_n[idx].astype(np.int8))
            rec['did_enter_lf'].append(enter_from_n[idx].astype(np.int8))
            rec['search_int_post'].append(new_search[idx])
            rec['got_offer'].append(has_offer[idx].astype(np.int8))
            rec['offered_wage'].append(offered_wage[idx])
            rec['did_accept'].append(accepts[idx].astype(np.int8))
            rec['was_separated'].append(is_separated[idx].astype(np.int8))
            rec['consumption'].append(consumption[idx])
            rec['savings'].append(savings[idx])
            rec['new_buffer'].append(new_buf[idx])
            rec['new_liq_type'].append(new_liq[idx])
            rec['new_debt_stress'].append(new_debt[idx])
            rec['new_emp_state'].append(cs[idx, CS_EMPLOYMENT])

        if (t % 60 == 0):
            print(f"  t={t}/{T}")

    # Concatenate
    for k in rec:
        rec[k] = np.concatenate(rec[k])

    elapsed = time.time() - t0
    print(f"Done: {len(rec['t'])} records, {elapsed:.1f}s")
    return rec


if __name__ == '__main__':
    os.makedirs('Phase3_Output', exist_ok=True)
    rec = collect_data(sample_n=10000, sample_interval=1, seed=42)
    np.savez_compressed('Phase3_Output/agent_decision_data.npz', **rec)
    print(f"Saved to Phase3_Output/agent_decision_data.npz")
    print(f"Total records: {len(rec['t']):,}")
    print(f"Columns: {len(rec)}")