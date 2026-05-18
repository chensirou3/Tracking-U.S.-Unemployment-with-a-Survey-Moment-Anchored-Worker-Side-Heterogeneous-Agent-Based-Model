# Mechanism Map — Phase 4

## 表1：机制总表

| # | Mechanism | Main Inputs | Intermediate Channel | Block | Aggregate Impact | Switch |
|---|-----------|-------------|---------------------|-------|-----------------|--------|
| 1 | high_fragility_modifier | fragility, buffer | 搜索方向(desperate/discouraged) | search, acceptance | UR, UE rate | ✅ |
| 2 | liquidity_constraint_modifier | liquidity_type | reservation wage折扣, MPC强制 | acceptance, consumption | UE rate, consumption | ✅ |
| 3 | housing_lockin_modifier | housing_status | 搜索半径缩小, flexibility cap | search, opportunity | UR, search intensity | ✅ |
| 4 | fragility_x_liquidity_interaction | fragility × liquidity | discouraged exit boost | participation | LFPR, UR | ✅ |
| 5 | matching_competition | search_int, mobility, flex | 有限岗位竞争分配 | opportunity | UR (最大影响) | ✅ |
| 6 | discouraged_worker | unemp_duration | 持续期>6月→exit跳升 | participation | LFPR, UR | ✅ |
| 7 | housing_reentry_friction | housing_status | owner re-entry惩罚 | participation | LFPR | ✅ |
| 8 | expectation_participation | income_expectation | 乐观→entry↑, 悲观→exit↑ | participation | LFPR | ✅ |
| 9 | effective_mpc_adjustment | liquidity, employment | H2M→MPC≈1, Wealthy→MPC×0.7 | consumption | consumption vol | ✅ |
| 10 | consumption_sequencing | consumption_type, buffer | Saver先压消费/Spender先耗buffer | consumption | buffer dynamics | ✅ |
| 11 | buffer_consumption_ordering | consumption_type | Spender允许负buffer(借贷) | borrowing | H2M share, debt | ✅ |
| 12 | state_dependent_expectation | employment, fragility | U→快速适应, E→慢速适应 | expectations | fragility spiral | ✅ |
| 13 | experience_dependent_expectation | employment transitions | 失业经历→预期下修→fragility↑ | expectations | fragility, UR | ✅ |

## 表2：异质性—机制映射表

| Heterogeneity | Labor Mechanisms | Household Mechanisms | Expectation Mechanisms |
|---------------|-----------------|---------------------|----------------------|
| Labor Fragility | #1 search direction, #4 exit boost | — | #12 update speed |
| Search Friction | #1 fragility×search, #5 competition | — | — |
| Housing Mobility | #3 lockin search, #7 reentry | — | — |
| Liquidity Fragility | #2 resv_wage discount | #9 MPC adjustment, #11 buffer ordering | — |
| Consumption Rule | — | #10 sequencing, #11 ordering | — |
| Income Expectation | #8 participation decision | #9 MPC link | #12,#13 update |

## 表3：Ablation 结果（recession scenario, 影响排序）

| Mechanism | ΔUR (关闭后-全开) | 方向 | 重要性 |
|-----------|------------------|------|--------|
| matching_competition | -3.15pp | 关闭→UR↓ | ⭐⭐⭐ 最大 |
| housing_reentry_friction | +2.72pp | 关闭→UR↑ | ⭐⭐⭐ |
| discouraged_worker | +2.32pp | 关闭→UR↑ | ⭐⭐⭐ |
| liquidity_constraint_modifier | +1.77pp | 关闭→UR↑ | ⭐⭐ |
| high_fragility_modifier | +1.40pp | 关闭→UR↑ | ⭐⭐ |
| experience_dependent_expectation | +1.33pp | 关闭→UR↑ | ⭐⭐ |
| state_dependent_expectation | -0.63pp | 关闭→UR↓ | ⭐ |
| housing_lockin_modifier | -0.56pp | 关闭→UR↓ | ⭐ |
| others | <0.5pp | 小 | — |

## 三条核心传导链

**链1：劳动冲击→消费响应**
separation_rate↑ → household_income↓ → cash_buffer↓ → liquidity downgrade(Buffer→H2M) → effective_mpc↑ → consumption↓

**链2：住房锁定→失业持续**
Owner-High-LTV → search_intensity↓ → offer_probability↓ → unemployment_duration↑ → discouraged worker exit

**链3：悲观螺旋**
Job loss → income_expectation↓ → labor_fragility↑ → search behavior change → worse outcomes → expectations further↓
