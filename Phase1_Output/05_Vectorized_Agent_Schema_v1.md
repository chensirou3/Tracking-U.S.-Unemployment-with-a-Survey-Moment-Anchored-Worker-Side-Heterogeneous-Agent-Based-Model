# 文档 5：向量化 Agent Schema v1

> 版本：v1.0
> 阶段：Phase 1 — Heterogeneity Audit & Engineering
> 设计目标：适合 NumPy 向量化实现的矩阵化 agent 结构

---

## 一、总体架构

每个 agent 的状态由 4 个矩阵的对应行组成。设 N = agent 数量（默认 100,000）。

```
Agent Population = {
    static_traits:      np.ndarray  shape (N, K_static)
    category_states:    np.ndarray  shape (N, K_cat)
    dynamic_states:     np.ndarray  shape (N, K_dyn)
    behavior_params:    np.ndarray  shape (N, K_behav)
}
```

**设计原则**：
1. 所有矩阵按行索引 agent（axis=0），按列索引字段（axis=1）
2. 决策规则通过向量化操作（广播、掩码、条件赋值）实现
3. 分类变量用 int 编码，连续变量用 float64
4. 不使用对象式 agent 实例

---

## 二、static_traits 矩阵

初始化一次，模拟期间**不更新**（age 除外，年度 +1）。

| 列索引 | 字段名 | dtype | 取值范围 | 来源 | 来自异质性 | 说明 |
|--------|--------|-------|---------|------|-----------|------|
| 0 | age | int16 | 18-85 | Core Q36 | 人口学 | 年度+1更新 |
| 1 | education | int8 | 0-4 | Core Q36 | 人口学 | 0=<HS, 1=HS, 2=Some College, 3=BA, 4=Graduate |
| 2 | marital_status | int8 | 0-2 | Core Q38 | 人口学 | 0=Single, 1=Married, 2=Other |
| 3 | household_size | int8 | 1-10 | Core Q39 | 人口学 | 家庭人数 |

**维度**：K_static = 4
**更新规则**：age 每 12 步（月）+1；其余不变
**广播**：全部按人存（per-agent），无组广播

---

## 三、category_states 矩阵

离散分类状态，更新频率从月度到年度不等。

| 列索引 | 字段名 | dtype | 取值编码 | 来源 | 来自异质性 | 更新频率 |
|--------|--------|-------|---------|------|-----------|---------|
| 0 | employment_state | int8 | 0=E, 1=U, 2=N | Core Q10 | 人口学/劳动 | 月度 |
| 1 | liquidity_type | int8 | 0=H2M, 1=Buffer, 2=Wealthy | Core Q32/33/47 | H3 | 季度（冲击时即时） |
| 2 | housing_status | int8 | 0=Renter-Mobile, 1=Renter-Stable, 2=Owner-Low-LTV, 3=Owner-High-LTV | Core Q41 + Housing HQH5 | H5 | 年度 |
| 3 | consumption_type | int8 | 0=Saver, 1=Smoother, 2=Spender | Spending qsp12n/13new | H6 | 不更新 |

**维度**：K_cat = 4
**更新规则**：
- employment_state：每步由劳动 block 决定（E↔U↔N 转移）
- liquidity_type：每季度根据 cash_buffer_months 重分类；负面冲击可即时触发降级
- housing_status：每年根据外生住房市场条件更新（低频）
- consumption_type：初始化后不变（慢偏好）

**向量化操作提示**：
- 状态转移用掩码实现：`mask_employed = category_states[:, 0] == 0`
- 条件更新：`category_states[mask_shock, 1] = 0  # 冲击后降级为H2M`

---

## 四、dynamic_states 矩阵

连续动态状态，每步或每几步更新。

| 列索引 | 字段名 | dtype | 取值范围 | 来源 | 来自异质性 | 更新频率 |
|--------|--------|-------|---------|------|-----------|---------|
| 0 | income_expectation | float64 | (-0.5, 0.5) | Core Q24_cent50 | H1 | 月度 |
| 1 | income_uncertainty | float64 | (0, 0.5) | Core Q24_iqr | H1 | 月度 |
| 2 | labor_fragility | float64 | [0, 1] | PCA(Q13new, 1-Q22new) | H2 | 季度 |
| 3 | cash_buffer_months | float64 | [0, 24+] | IW Q6分布校准 | H3 | 季度（冲击即时） |
| 4 | search_intensity | float64 | [0, 40+] | LM js7 | H4 | 季度 |
| 5 | mobility_friction_score | float64 | [0, 1] | Housing HQH6 | H5 | 年度 |
| 6 | household_income | float64 | (0, ∞) | Core Q4new | 人口学 | 月度 |
| 7 | unemployment_duration | float64 | [0, ∞) | LM l8 | 人口学 | 月度（仅U状态+1） |
| 8 | debt_stress | float64 | [0, 1] | 派生 | 派生 | 季度 |

**维度**：K_dyn = 9
**更新规则**：
- income_expectation/uncertainty：每步根据宏观信号和个体经历更新（预期更新规则）
- labor_fragility：每季度根据宏观劳动市场条件和个体状态更新
- cash_buffer_months：每季度根据收入-支出差额更新；负面冲击可即时消耗
- search_intensity：每季度更新（仅 U 状态 agent 有意义）
- mobility_friction_score：每年更新（慢变量）
- household_income：每步由就业状态和工资过程决定
- unemployment_duration：U 状态每步+1；E/N 状态归零
- debt_stress：每季度由借贷 block 更新

**向量化操作提示**：
- 仅更新失业者的搜索强度：`dynamic_states[mask_unemployed, 4] = new_search`
- 缓冲消耗：`dynamic_states[:, 3] -= monthly_expense * mask_no_income`


---

## 五、behavior_params 矩阵

行为参数，初始化后极少更新（慢偏好或规则参数）。

| 列索引 | 字段名 | dtype | 取值范围 | 来源 | 来自异质性 | 更新频率 |
|--------|--------|-------|---------|------|-----------|---------|
| 0 | mpc_positive | float64 | [0, 1] | Spending qsp12n | H6 | 不更新 |
| 1 | mpc_negative | float64 | [0, 1] | Spending qsp13new | H6 | 不更新 |
| 2 | asymmetry_ratio | float64 | [0, ∞) | 派生: mpc_neg/mpc_pos | H6 | 不更新 |
| 3 | reservation_wage_ratio | float64 | [0.5, 3.0] | LM rw2/wage | H4 | 季度 |
| 4 | flexibility_index | float64 | [-3, 3] | PCA(rw3b,rw4b,rw6b) | H4 | 年度 |

**维度**：K_behav = 5
**更新规则**：
- mpc_positive/negative/asymmetry_ratio：初始化后不变（慢偏好）
- reservation_wage_ratio：每季度根据劳动市场条件和失业持续期微调
- flexibility_index：每年微调（极慢变量）

**向量化操作提示**：
- 消费响应：`delta_c = shock * np.where(shock > 0, bp[:, 0], bp[:, 1])`
- 保留工资：`resv_wage = current_wage * bp[:, 3]`

---

## 六、矩阵维度汇总

| 矩阵名 | 形状 | 总字段数 | dtype主体 | 更新频率 |
|--------|------|---------|----------|---------|
| static_traits | (N, 4) | 4 | int8/int16 | 基本不更新 |
| category_states | (N, 4) | 4 | int8 | 月度~年度 |
| dynamic_states | (N, 9) | 9 | float64 | 月度~年度 |
| behavior_params | (N, 5) | 5 | float64 | 基本不更新~季度 |
| **总计** | **(N, 22)** | **22** | — | — |

N=100,000 时总内存 ≈ 100,000 × 22 × 8 bytes ≈ **17.6 MB**，完全可在 CPU 内存中高效运算。

---

## 七、扩展预留接口

以下字段在 MVP 阶段**不创建**，但在矩阵设计中预留扩展位置。

| 矩阵 | 字段名 | 来自异质性 | 引入时机 |
|------|--------|-----------|---------|
| dynamic_states | inflation_expectation | H7 Inflation Belief | 阶段4+（工资模块） |
| dynamic_states | inflation_uncertainty | H7 Inflation Belief | 阶段4+ |
| category_states | credit_status | H8 Credit Access | 阶段4+（借贷扩展） |
| dynamic_states | credit_approval_belief | H8 Credit Access | 阶段4+ |
| static_traits | numeracy_score | H9 Numeracy | 阶段4+（预期质量） |
| static_traits | risk_aversion | H10 Risk Preference | 阶段4+（资产选择） |

扩展通过 `np.column_stack` 或预分配更大矩阵实现。

---

## 八、字段索引常量定义（建议）

```python
# === static_traits 列索引 ===
ST_AGE = 0;  ST_EDUCATION = 1;  ST_MARITAL = 2;  ST_HH_SIZE = 3

# === category_states 列索引 ===
CS_EMPLOYMENT = 0;  CS_LIQUIDITY_TYPE = 1
CS_HOUSING_STATUS = 2;  CS_CONSUMPTION_TYPE = 3

# === dynamic_states 列索引 ===
DS_INCOME_EXP = 0;  DS_INCOME_UNC = 1;  DS_LABOR_FRAG = 2
DS_CASH_BUFFER = 3;  DS_SEARCH_INT = 4;  DS_MOBILITY_FRIC = 5
DS_HH_INCOME = 6;  DS_UNEMP_DUR = 7;  DS_DEBT_STRESS = 8

# === behavior_params 列索引 ===
BP_MPC_POS = 0;  BP_MPC_NEG = 1;  BP_ASYMMETRY = 2
BP_RESV_WAGE = 3;  BP_FLEXIBILITY = 4

# === 编码常量 ===
EMP_E, EMP_U, EMP_N = 0, 1, 2
LIQ_H2M, LIQ_BUFFER, LIQ_WEALTHY = 0, 1, 2
HSG_RENT_MOB, HSG_RENT_STB, HSG_OWN_LOW, HSG_OWN_HIGH = 0, 1, 2, 3
CON_SAVER, CON_SMOOTHER, CON_SPENDER = 0, 1, 2
```

---

## 九、初始化流程概要（阶段 2 入口）

```
1. static_traits（无依赖）
   age ← 人口普查年龄分布
   education ← SCE 教育分布 | age
   marital_status ← SCE | age
   household_size ← SCE | marital_status

2. category_states（依赖 static_traits）
   employment_state ← BLS E/U/N 比例 | age, education
   liquidity_type ← Core Q32/33/47 规则 | income, employment
   housing_status ← Core Q41 + Housing | age, income
   consumption_type ← Spending latent class

3. dynamic_states（依赖 static_traits + category_states）
   income_expectation ← Q24_cent50 | employment, education
   income_uncertainty ← Q24_iqr | income_expectation
   labor_fragility ← PCA分数 | employment, age
   cash_buffer_months ← IW Q6校准 | liquidity_type
   search_intensity ← js7 | employment_state (仅U)
   mobility_friction_score ← HQH6 | housing_status
   household_income ← Q4new | employment, education, age
   unemployment_duration ← l8 | employment_state (仅U)
   debt_stress ← 派生 | liquidity_type

4. behavior_params（依赖 category_states）
   mpc_positive ← qsp12n/100 | liquidity_type
   mpc_negative ← qsp13new/100 | liquidity_type
   asymmetry_ratio ← 派生
   reservation_wage_ratio ← rw2/wage | employment, education
   flexibility_index ← PCA | housing_status, age
```

**关键**：顺序有依赖。1→2→3/4。

---

## 十、通过标准自检

| 检查项 | 状态 |
|--------|------|
| 每个 MVP 异质性都有对应的矩阵字段 | ✅ |
| 每个字段的 dtype 已定义 | ✅ |
| 每个字段的更新频率已定义 | ✅ |
| 按人存 vs 按组广播已说明 | ✅ 全部按人存 |
| 初始化顺序和条件依赖已说明 | ✅ |
| 扩展字段已预留 | ✅ |
| N=100,000 时内存可行性已验证 | ✅ ~17.6 MB |
| 阶段 2 可直接基于本 Schema 开始人口生成 | ✅ |