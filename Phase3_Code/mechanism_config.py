"""
Module H: Mechanism Configuration
Provides on/off switches and parameter hooks for all structural mechanisms.
When a mechanism is disabled, the block falls back to Phase 3 simplified logic.
"""


def default_config():
    """Return default mechanism configuration with all mechanisms ON."""
    return {
        # --- Module B: Type-Specific Behavior ---
        'high_fragility_modifier': {
            'enabled': True,
            'description': 'High fragility agents have state-dependent search/acceptance behavior',
            'fragility_threshold': 0.5,
            'search_desperation_buffer_threshold': 1.0,
            'acceptance_pressure_factor': 0.15,
            'blocks_affected': ['search', 'acceptance'],
        },
        'liquidity_constraint_modifier': {
            'enabled': True,
            'description': 'H2M agents face forced MPC near 1.0 and lower reservation wage',
            'h2m_mpc_floor': 0.90,
            'h2m_resv_wage_discount': 0.20,
            'blocks_affected': ['acceptance', 'consumption'],
        },
        'housing_lockin_modifier': {
            'enabled': True,
            'description': 'Owner-High-LTV agents have reduced search radius and flexibility',
            'lockin_search_penalty': 0.30,
            'lockin_flexibility_cap': 0.0,
            'blocks_affected': ['search', 'opportunity'],
        },
        'fragility_x_liquidity_interaction': {
            'enabled': True,
            'description': 'High fragility + H2M triggers discouraged exit',
            'discouraged_exit_boost': 0.05,
            'blocks_affected': ['participation'],
        },

        # --- Module C: Matching Competition ---
        'matching_competition': {
            'enabled': True,
            'description': 'Finite vacancy pool with competitive allocation',
            'vacancy_rate': 0.03,
            'blocks_affected': ['opportunity'],
        },

        # --- Module D: Exit / Re-entry ---
        'discouraged_worker': {
            'enabled': True,
            'description': 'Duration-dependent discouragement with heterogeneous thresholds',
            'duration_threshold_months': 6,
            'exit_jump_factor': 2.0,
            'blocks_affected': ['participation'],
        },
        'housing_reentry_friction': {
            'enabled': True,
            'description': 'Housing lock-in affects labor force re-entry',
            'owner_reentry_penalty': 0.30,
            'blocks_affected': ['participation'],
        },
        'expectation_participation': {
            'enabled': True,
            'description': 'Income expectation affects participation decision',
            'optimism_entry_boost': 0.3,
            'pessimism_exit_boost': 0.2,
            'blocks_affected': ['participation'],
        },

        # --- Module E: Consumption Adjustment ---
        'effective_mpc_adjustment': {
            'enabled': True,
            'description': 'Effective MPC dynamically adjusts with liquidity and employment state',
            'h2m_mpc_floor': 0.95,
            'wealthy_mpc_discount': 0.30,
            'unemployed_mpc_boost': 0.10,
            'blocks_affected': ['consumption'],
        },
        'consumption_sequencing': {
            'enabled': True,
            'description': 'Different consumption types follow different adjustment sequences',
            'saver_buffer_protect_threshold': 3.0,
            'spender_buffer_use_first': True,
            'blocks_affected': ['consumption', 'borrowing'],
        },

        # --- Module F: Borrowing-Buffer Interaction ---
        'buffer_consumption_ordering': {
            'enabled': True,
            'description': 'Type-dependent ordering: buffer first vs cut consumption first',
            'stress_feedback_rate': 0.08,
            'max_negative_buffer': -2.0,
            'blocks_affected': ['borrowing'],
        },

        # --- Module G: Expectation Updating ---
        'state_dependent_expectation': {
            'enabled': True,
            'description': 'Expectation update speed depends on employment state and fragility',
            'job_loss_revision_factor': 0.15,
            'high_fragility_gain_boost': 1.5,
            'employed_adaptation_speed': 0.05,
            'unemployed_adaptation_speed': 0.20,
            'blocks_affected': ['expectations'],
        },
        'experience_dependent_expectation': {
            'enabled': True,
            'description': 'Personal labor market experience feeds back to expectations',
            'experience_weight': 0.10,
            'blocks_affected': ['expectations'],
        },
    }


def all_off_config():
    """Return config with all mechanisms OFF (Phase 3 fallback)."""
    cfg = default_config()
    for k in cfg:
        cfg[k]['enabled'] = False
    return cfg


def ablation_config(mechanism_to_disable):
    """Return config with one specific mechanism disabled."""
    cfg = default_config()
    if mechanism_to_disable in cfg:
        cfg[mechanism_to_disable]['enabled'] = False
    return cfg
