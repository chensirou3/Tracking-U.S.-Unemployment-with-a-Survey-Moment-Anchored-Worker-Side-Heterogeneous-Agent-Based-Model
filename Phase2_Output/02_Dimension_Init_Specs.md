# Dimension Initialization Specs（含分布计算协议）

> 版本：v1.0 | 阶段：Phase 2

---

## 分布计算协议总表

| 异质性 | 分布类型 | 分布对象 | 估计方法 | 初始化方法 | 需要 Update Rule | Agent Container |
|--------|---------|---------|---------|-----------|-----------------|----------------|
| H1 Income Growth Exp | 第五类(动态状态) | 条件经验连续分布 | Q24_cent50/iqr 按组经验分布 | 条件抽样 | ✅ 月度 | dynamic_states |
| H2 Labor Fragility | 第五类(动态状态) | 因子分数经验分布 | PCA(Q13new, 1-Q22new) | 条件抽样 | ✅ 季度 | dynamic_states |
| H3 Liquidity Fragility | 第三类(条件型连续) | 类别比例 + 组内连续 | Q33规则分类 + buffer校准 | 两步法 | ✅ 季度+冲击即时 | cat_states + dyn_states |
| H4 Labor Search Friction | 第四类(规则型)+第三类 | 参数组条件分布 | rw2h/js7 按组经验分布 | 参数组初始化 | ✅ 季度 | behav_params + dyn_states |
| H5 Housing Mobility | 第三类(条件型连续) | 类别比例 + 组内连续 | own_rent分类 + mobility构造 | 两步法 | ⚠️ 年度 | cat_states + dyn_states |
| H6 Consumption Adj | 第四类(规则型) | 类型概率 + 参数分布 | qsp12n/qsp13new → 类型+参数 | 类型+参数组 | ✅ 有效MPC随状态调节 | behav_params + cat_states |

---

## H1: Income Growth Expectation

**分布类型**：第五类（动态状态型）

**经验分布参数**（从 Core Q24_cent50）：
- n = 80,159 | mean = 3.05% | std = 4.91% | median = 2.30%
- p10 = -1.3% | p25 = 0.62% | p75 = 4.49% | p90 = 7.79%
- 分布特征：右偏、厚右尾，有少量负值

**条件分组**：按 employment_state × income_tier
- E 组：median ≈ 2.5%, std ≈ 4.2%（较集中）
- U 组：median ≈ 1.5%, std ≈ 6.5%（更分散，更悲观）
- N 组：median ≈ 1.0%, std ≈ 5.0%

**不确定性**（Q24_iqr）：
- mean = 3.12 | std = 3.95 | median = 1.38
- 高不确定性与低收入、低教育相关

**初始化**：
1. 按 employment_state 分组
2. 组内从 Q24_cent50 经验分布 KDE 抽样（截断在 [-30, 50]）
3. Q24_iqr 条件于 Q24_cent50 分位数抽样

**Agent 字段**：dynamic_states[:, 0] = income_expectation (Q24_cent50/100)
                dynamic_states[:, 1] = income_uncertainty (Q24_iqr/100)

---

## H2: Labor Fragility

**分布类型**：第五类（动态状态型）

**经验分布参数**：
- Q13new (失业概率 0-100)：mean=14.8, std=20.3, median=7.0
  - p10=0, p25=2, p50=7, p75=15, p90=40
  - 极度右偏：多数人自评低风险，少数人极高
- Q22new (再就业概率 0-100)：mean=54.6, std=32.1, median=52.0
  - 分布较对称但方差大

**构造**：
1. 反转 Q22new → reemploy_difficulty = (100 - Q22new) / 100
2. job_loss_prob = Q13new / 100
3. fragility_index = (job_loss_prob + reemploy_difficulty) / 2
4. 结果范围 [0, 1]，mean ≈ 0.30, median ≈ 0.26

**条件分组**：按 employment_state × age_cat
- E+Young：fragility 较低（mean ≈ 0.22）
- E+Old：fragility 中等（mean ≈ 0.28，再就业难度高）
- U：fragility 高（mean ≈ 0.55）
- N：不适用，设为 0.5（退出者不面临劳动市场风险但缓冲弱）

**初始化**：按 employment × age 分组，组内从 fragility_index 经验分布抽样
**Agent 字段**：dynamic_states[:, 2] = labor_fragility

---

## H3: Liquidity Fragility

**分布类型**：第三类（条件型连续）

**第一步——类别分布**：
- Q33=2 (No, 无法覆盖3月): ~51% → 含 H2M 和部分 Buffer
- Q33=1 (Yes): ~49%
- 结合 Kaplan-Violante → H2M: 30%, Buffer: 45%, Wealthy: 25%

**第二步——组内 cash_buffer_months**：
- H2M：0-1 个月（mean=0.5, std=0.3）
- Buffer：1-6 个月（mean=3.0, std=1.5）
- Wealthy：6-24 个月（mean=12.0, std=4.0）
- 参考 Informal Work Q6 的 5 档分布校准

**条件化**：liquidity_type 条件于 employment × housing_status
- U × Renter → H2M 概率更高（~50%）
- E × Owner-Low-LTV → Wealthy 概率更高（~40%）

**初始化**：
1. 按 employment × housing 条件赋 liquidity_type
2. 组内从 truncated normal 抽 cash_buffer_months

**Agent 字段**：
- category_states[:, 1] = liquidity_type
- dynamic_states[:, 3] = cash_buffer_months

---

## H4: Labor Search Friction

**分布类型**：第四类（规则型）+ 第三类

**经验分布**：
- rw2h_reserv_wage (时薪)：median=$21.6, p25=$15, p75=$36
- reservation_wage_ratio ≈ rw2h / median_wage ≈ 1.0（中位数约等于市场工资）
- rw3b (搬迁加薪%)：median 很高（999998=不接受），需清洗
- rw4b (通勤加薪%)：median=400（需确认编码，可能是4%→编码×100）
- l7_days_spent_searching：median=63 天→约 9 周

**构造**：
- reservation_wage_ratio = rw2h / group_median_wage → [0.5, 3.0]
- search_intensity：基于 l7 按搜索天数标准化到 [0, 40] 小时/周
- flexibility_index：基于 rw3/rw4/rw6 清洗后 PCA → [-3, 3]

**条件化**：按 employment_state（仅 U 和部分 E 在搜索）
- E 状态：search_intensity = 0（不搜索），但保留 reservation_wage
- U 状态：search_intensity 从经验分布抽样
- N 状态：search_intensity = 0，reservation_wage 设为高值

**Agent 字段**：
- behavior_params[:, 3] = reservation_wage_ratio
- dynamic_states[:, 4] = search_intensity
- behavior_params[:, 4] = flexibility_index


---

## H5: Housing Mobility Friction

**分布类型**：第三类（条件型连续）

**第一步——类别分布**（housing_status 已在骨架中生成）：
- Renter-Mobile: 12% | Renter-Stable: 20% | Owner-Low-LTV: 45% | Owner-High-LTV: 23%

**第二步——组内 mobility_friction_score [0,1]**：
- Renter-Mobile：低摩擦（mean=0.15, std=0.10）
- Renter-Stable：中低摩擦（mean=0.35, std=0.15）
- Owner-Low-LTV：中高摩擦（mean=0.60, std=0.15）
- Owner-High-LTV：高摩擦（mean=0.80, std=0.10）

**初始化**：按 housing_status 分组，组内从 truncated normal [0,1] 抽样
**Agent 字段**：dynamic_states[:, 5] = mobility_friction_score

---

## H6: Consumption Adjustment Rule

**分布类型**：第四类（规则型）

**经验分布**（qsp12n/qsp13new 1-7编码 → 转换为 MPC [0,1]）：
- mpc_positive = (qsp12n-1)/6 → mean≈0.47, std≈0.30（双峰）
- mpc_negative = (qsp13new-1)/6 → mean≈0.29, std≈0.30（左偏）

**类型分类**（条件于 liquidity_type）：
- Saver (30%): mpc_pos<0.3 | H2M→Spender↑, Wealthy→Saver↑
- Smoother (40%): 0.3≤mpc_pos≤0.7
- Spender (30%): mpc_pos>0.7

**有效 MPC 动态调节**（阶段 3 实现）：effective_mpc = base_mpc × liquidity_factor

**初始化**：
1. 按 liquidity_type 条件赋 consumption_type
2. 组内抽 mpc_positive, mpc_negative
3. 派生 asymmetry_ratio = mpc_negative / max(mpc_positive, 0.01)

**Agent 字段**：
- category_states[:, 3] = consumption_type
- behavior_params[:, 0-2] = mpc_positive, mpc_negative, asymmetry_ratio