# State Transition Map

> Phase 3 — Main Model Core Engine

## 表 1：状态变量更新表

| State Variable | Matrix[Col] | Updated By | Frequency | Notes |
|----------------|-------------|-----------|-----------|-------|
| employment_state | cs[0] | labor transitions (Step 7) | 月度 | E↔U↔N 核心状态机 |
| liquidity_type | cs[1] | borrowing block (Step 10) | 月度 | 升降级规则 |
| housing_status | cs[2] | — | 不更新(v1) | 阶段4加入 |
| consumption_type | cs[3] | — | 不更新 | 底层偏好 |
| income_expectation | ds[0] | update_expectations (Step 2) | 月度 | 向背景值适应 |
| income_uncertainty | ds[1] | update_expectations (Step 2) | 月度 | 环境恶化时上升 |
| labor_fragility | ds[2] | update_expectations (Step 2) | 月度 | E:↓, U:↑ |
| cash_buffer_months | ds[3] | borrowing block (Step 10) | 月度 | savings → buffer |
| search_intensity | ds[4] | search block (Step 4) | 月度 | 仅U有效 |
| mobility_friction | ds[5] | — | 不更新(v1) | 阶段4加入 |
| household_income | ds[6] | update_income (Step 8) | 月度 | 受就业状态驱动 |
| unemployment_dur | ds[7] | labor transitions (Step 7) | 月度 | U:+1, 其他:0 |
| debt_stress | ds[8] | borrowing block (Step 10) | 月度 | 缓冲不足时上升 |
| mpc_positive | bp[0] | — | 不更新(v1) | 阶段4加入状态调节 |
| mpc_negative | bp[1] | — | 不更新(v1) | 阶段4加入状态调节 |
| asymmetry_ratio | bp[2] | — | 不更新 | 派生 |
| reservation_wage | bp[3] | — | 不更新(v1) | acceptance中做临时decay |
| flexibility_index | bp[4] | — | 不更新(v1) | 阶段4加入 |

## 表 2：决策模块输入输出表

| Block | Inputs | Outputs | States Changed | Affected Aggregates |
|-------|--------|---------|---------------|-------------------|
| Participation | emp, age, frag, inc_exp, cash_buf | exit_to_n, enter_from_n | (间接via Step7) emp | LFPR, EPOP |
| Search | emp, frag, mob_fric, dur, cash_buf, flex, env | search_intensity | ds[4] | avg_search |
| Opportunity | emp, search_int, mob_fric, flex, frag, env | has_offer, wage, is_separated | (间接via Step7) | UR, EU/UE rates |
| Acceptance | emp, resv_wage, dur, cash_buf, frag, offer | accepts | (间接via Step7) | UE rate |
| Consumption | emp, income, mpc, liq_type, con_type | consumption, savings | — | avg_income |
| Borrowing | liq_type, cash_buf, debt, savings, env | new_buffer, new_liq, new_debt | ds[3], cs[1], ds[8] | H2M share, buffer |

## 劳动状态转移图

```
         separation (1.2%/mo)
    E ──────────────────────→ U
    ↑                         │
    │ acceptance (14%/mo)     │ discouraged (2%/mo)
    │←────────────────────────│
    │                         ↓
    │    entry (1.5%/mo)      N
    │←────────────────────────│
    │  voluntary exit (0.5%/mo)
    └─────────────────────────→ N
```
