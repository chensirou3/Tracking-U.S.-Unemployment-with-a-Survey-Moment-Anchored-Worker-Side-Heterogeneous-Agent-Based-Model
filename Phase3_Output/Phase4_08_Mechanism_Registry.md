# Mechanism Registry

## 表：机制接口标准化

| # | Mechanism | Inputs | Outputs | States Changed | Calibration Hook | Ablation Ready |
|---|-----------|--------|---------|---------------|-----------------|---------------|
| 1 | high_fragility_modifier | fragility, buffer, fragility_threshold | search direction, acceptance pressure | ds[search_int] | fragility_threshold, acceptance_pressure_factor | ✅ |
| 2 | liquidity_constraint_modifier | liquidity_type | resv_wage discount, mpc floor | bp[resv_wage], effective mpc | h2m_resv_wage_discount, h2m_mpc_floor | ✅ |
| 3 | housing_lockin_modifier | housing_status | search penalty, flex cap | ds[search_int] | lockin_search_penalty | ✅ |
| 4 | fragility_x_liquidity_interaction | fragility, liquidity_type | exit probability boost | (via participation) | discouraged_exit_boost | ✅ |
| 5 | matching_competition | search_int, mobility_fric, flexibility | offer allocation | has_offer | vacancy_rate | ✅ |
| 6 | discouraged_worker | unemp_duration | exit jump after threshold | (via participation) | duration_threshold_months, exit_jump_factor | ✅ |
| 7 | housing_reentry_friction | housing_status | re-entry penalty | (via participation) | owner_reentry_penalty | ✅ |
| 8 | expectation_participation | income_expectation | entry/exit probability mod | (via participation) | optimism_entry_boost, pessimism_exit_boost | ✅ |
| 9 | effective_mpc_adjustment | liquidity_type, employment | effective MPC | (via consumption) | h2m_mpc_floor, wealthy_mpc_discount, unemployed_mpc_boost | ✅ |
| 10 | consumption_sequencing | consumption_type, buffer | MPC modification | (via consumption) | saver_buffer_protect_threshold | ✅ |
| 11 | buffer_consumption_ordering | consumption_type, savings | buffer change, stress | ds[cash_buffer], ds[debt_stress] | max_negative_buffer, stress_feedback_rate | ✅ |
| 12 | state_dependent_expectation | employment, fragility | expectation update speed | ds[income_exp] | employed/unemployed_adaptation_speed, high_fragility_gain_boost | ✅ |
| 13 | experience_dependent_expectation | employment transitions | expectation revision, fragility feedback | ds[income_exp], ds[labor_frag] | experience_weight, job_loss_revision_factor | ✅ |

## 开关配置

所有机制的开关在 `Phase3_Code/mechanism_config.py` 中定义。

使用方式：
```python
from Phase3_Code.mechanism_config import default_config, all_off_config, ablation_config

cfg = default_config()           # 全部开启
cfg = all_off_config()           # 全部关闭（Phase 3 fallback）
cfg = ablation_config('matching_competition')  # 关闭单个机制
```

## 参数优先级表

| 参数 | 当前值 | 可调范围 | 对UR影响方向 | 优先级 |
|------|--------|---------|-------------|--------|
| vacancy_rate | 0.03 | [0.01, 0.08] | ↑vacancy→↓UR | ⭐⭐⭐ |
| duration_threshold_months | 6 | [3, 12] | ↓threshold→↓UR(via LFPR) | ⭐⭐⭐ |
| exit_jump_factor | 2.0 | [1.0, 4.0] | ↑jump→↓UR(via LFPR) | ⭐⭐ |
| owner_reentry_penalty | 0.30 | [0.0, 0.6] | ↑penalty→↓LFPR | ⭐⭐ |
| h2m_resv_wage_discount | 0.20 | [0.0, 0.5] | ↑discount→↓UR | ⭐⭐ |
| fragility_threshold | 0.5 | [0.3, 0.7] | 影响双向搜索分界 | ⭐ |
| acceptance_pressure_factor | 0.15 | [0.0, 0.4] | ↑pressure→↓UR | ⭐ |
