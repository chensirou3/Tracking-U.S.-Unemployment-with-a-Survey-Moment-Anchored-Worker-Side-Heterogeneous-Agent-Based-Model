# Joint Structure Specification

> 版本：v1.0 | 阶段：Phase 2

---

## 一、必须保证的 5 对联合关系

| # | 变量 A | 变量 B | 关系类型 | 预期方向 | 实现方式 | 验证方法 |
|---|--------|--------|---------|---------|---------|---------|
| 1 | Labor Fragility | Income Growth Exp | 负相关 | 高脆弱 → 更悲观 | 条件抽样 | Spearman 相关 < 0 |
| 2 | Liquidity Type | Consumption Type | 正关联 | H2M → Spender↑ | 条件概率表 | 交叉频率表 χ² |
| 3 | Housing Status | Search Friction | 正关联 | Owner-High → 高摩擦 | 条件抽样 | 组间均值差异 |
| 4 | Housing Status | Liquidity Type | 结构关联 | Owner → Wealthy↑ | 条件概率表 | 交叉频率表 |
| 5 | Employment State | Search Params | 状态依赖 | U → 高搜索强度 | 条件赋值 | 组间均值差异 |

---

## 二、联合关系实现细节

### 关系 1：Labor Fragility × Income Growth Expectation

**机制**：高失业风险者对未来收入更悲观或更不确定。

**实现**：
1. 生成 labor_fragility 后，按分位数分为 5 组
2. income_expectation 按 fragility 分位组条件抽样
3. 高 fragility 组：从 Q24_cent50 的 p10-p50 区间抽（更多负值/低值）
4. 低 fragility 组：从 Q24_cent50 的 p50-p90 区间抽

**目标**：Spearman ρ(fragility, income_exp) ≈ -0.25 到 -0.40

### 关系 2：Liquidity Type × Consumption Type

**机制**：流动性不足者 MPC 更高（Kaplan-Violante 核心预测）。

**实现**：条件概率表

| | Saver | Smoother | Spender |
|---|------|---------|---------|
| H2M | 10% | 30% | 60% |
| Buffer | 25% | 50% | 25% |
| Wealthy | 55% | 35% | 10% |

### 关系 3：Housing Status × Labor Search Friction

**机制**：住房锁定限制地理搜索范围 → 搜索摩擦更高。

**实现**：
1. Owner-High-LTV 的 flexibility_index 从低灵活性区间抽样
2. Renter-Mobile 的 flexibility_index 从高灵活性区间抽样
3. reservation_wage_ratio 也条件于 housing_status（owner 有房贷压力 → 可能降低保留工资）

### 关系 4：Housing Status × Liquidity Type

**机制**：owner 有不动产但可能缺流动性（Wealthy H2M）；renter 可能有流动性但无资产。

**实现**：条件概率表

| | H2M | Buffer | Wealthy |
|---|-----|--------|---------|
| Renter-Mobile | 45% | 45% | 10% |
| Renter-Stable | 40% | 45% | 15% |
| Owner-Low-LTV | 15% | 45% | 40% |
| Owner-High-LTV | 35% | 45% | 20% |

### 关系 5：Employment State × Search Parameters

**机制**：就业状态决定搜索行为。

**实现**：
- E 状态：search_intensity = 0（不积极搜索），reservation_wage 从工作者分布抽
- U 状态：search_intensity 从 LM js7/l7 经验分布抽，reservation_wage 随失业持续期下降
- N 状态：search_intensity = 0，reservation_wage 设为极高值（表示不搜索）

---

## 三、生成顺序（保证联合结构）

```
Step 1: static_traits (age, education, marital, hh_size)
           ↓ 无条件，独立或弱条件
Step 2: employment_state  ← 条件于 age × education
           ↓
Step 3: housing_status    ← 条件于 age × income_proxy
           ↓
Step 4: liquidity_type    ← 条件于 employment × housing (关系 4)
           ↓
Step 5: consumption_type  ← 条件于 liquidity_type (关系 2)
           ↓
Step 6: labor_fragility   ← 条件于 employment × age
           ↓
Step 7: income_expectation ← 条件于 labor_fragility (关系 1)
           ↓
Step 8: search_params     ← 条件于 employment × housing (关系 3, 5)
           ↓
Step 9: mpc_params        ← 条件于 consumption_type
           ↓
Step 10: remaining fields ← 条件于已有状态
```

**关键**：顺序不可随意更改。每一步的条件依赖于前面已生成的变量。

---

## 四、验证清单

| 验证项 | 指标 | 通过标准 |
|--------|------|---------|
| fragility-income_exp 相关 | Spearman ρ | -0.45 < ρ < -0.15 |
| liquidity-consumption 关联 | χ² p-value | p < 0.001 |
| housing-flexibility 组间差 | t-test | Owner > Renter (p < 0.01) |
| housing-liquidity 关联 | χ² p-value | p < 0.001 |
| search_intensity E vs U | mean diff | U >> E ≈ 0 |
| E/U/N 总比例 | 比例 | E:60%, U:4%, N:36% (±2%) |
| Owner/Renter 总比例 | 比例 | Owner:68%, Renter:32% (±3%) |
| H2M 总比例 | 比例 | 28-33% |
