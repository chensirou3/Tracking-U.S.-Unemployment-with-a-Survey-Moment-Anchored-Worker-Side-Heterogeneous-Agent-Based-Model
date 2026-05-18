# 文档 3：异质性字典 v2（Heterogeneity Dictionary v2）

> 版本：v2.0
> 阶段：Phase 1 — Heterogeneity Audit & Engineering
> 基于 v1 审计结果修订

---

## 类型分类说明

每个异质性被标注为以下工程类型之一：

| 类型代码 | 含义 | 在 NumPy 中的典型表示 |
|---------|------|---------------------|
| `continuous` | 连续数值变量 | float64 |
| `categorical` | 离散分类状态 | int8 |
| `conditional_continuous` | 仅在特定条件下有意义的连续变量 | float64 + mask |
| `dynamic_state` | 每期更新的动态状态 | float64, 逐期覆写 |
| `rule_based` | 决定行为规则类型的参数 | int8 (类型) + float64 (参数) |

---

## 第一圈：MVP 主系统（6 维）

---

### H1: Income Growth Expectation

| 属性 | 值 |
|------|-----|
| **全称** | Income Growth Expectation & Uncertainty |
| **层级** | 第一圈 MVP |
| **主类别** | 预期（Expectation） |
| **工程类型** | `dynamic_state` (continuous) |
| **时间属性** | 快速预期变量，月度更新 |
| **Agent Container** | `dynamic_states` |

**机制摘要**：收入增长预期直接影响 (1) 消费-储蓄分配，(2) 求职强度与保留工资，(3) 借贷意愿，(4) 劳动参与决策。

**问卷来源**：

| 角色 | 模块 | 题号 | 说明 |
|------|------|------|------|
| 主支持 | Core | Q24_cent25/50/75, Q24_var, Q24_mean, Q24_iqr | 1年期家庭收入增长密度预测 |
| 主支持 | Core | Q25v2/Q25v2part2 | 预期收入变化方向和幅度 |
| 辅助 | Core | Q4new | 过去12个月家庭总收入 |
| 辅助 | Core | Q28/Q29/Q30new | 主观财务状况评估（当前/过去/未来） |
| 辅助 | Spending | HH Finance b4/b5 | 过去12个月收入变化 |

**主加载**：→ Income Growth Expectation
**次加载**：Q28/Q29 → Liquidity Fragility; Q4new → Balance Sheet Composition

**构造方法**：
1. 核心指标：Q24_cent50（预期中位数增长率）→ 连续变量
2. 不确定性：Q24_iqr → 连续变量
3. 可选增强：构造 optimist/pessimist/uncertain 三类 latent class（基于 Q24_cent50 × Q24_iqr 联合分布）

**分布对象**：
- 主分布：empirical continuous distribution of Q24_cent50
- 辅助分布：conditional distribution of Q24_iqr | Q24_cent50
- 适合直接用于初始化

**影响的决策模块**：
- Consumption-smoothing block（消费-储蓄分配）
- Search block（搜索强度调节）
- Acceptance block（保留工资修正）
- Participation block（劳动参与决策）

---

### H2: Labor Fragility

| 属性 | 值 |
|------|-----|
| **全称** | Labor Fragility — 就业脆弱性与劳动市场风险暴露 |
| **层级** | 第一圈 MVP |
| **主类别** | 状态（State）+ 预期（Expectation） |
| **工程类型** | `dynamic_state` (continuous index) |
| **时间属性** | 中速状态变量，季度更新 |
| **Agent Container** | `dynamic_states` |

**机制摘要**：就业脆弱性直接决定 (1) 失业概率，(2) 再就业能力，(3) 预防性储蓄动机，(4) 消费抑制程度。

**问卷来源**：

| 角色 | 模块 | 题号 | 说明 |
|------|------|------|------|
| 主支持 | Core | Q13new | 未来12个月失去当前工作的概率 |
| 主支持 | Core | Q22new | 如果失业，4个月内找到工作的概率 |
| 主支持 | LM | ec14_cps_job_layoff_chance | 被裁概率 |
| 辅助 | LM | l8_months_no_work | 无工作月数 |
| 辅助 | LM | ec13_cps_job_job_satisfied | 工作满意度 |
| 辅助 | Core | Q15/Q16 | 自愿离职概率 |
| 辅助 | LM | ec9/ec10/ec11/ec12 | 工资/福利/技能匹配/晋升满意度 |

**主加载**：→ Labor Fragility
**次加载**：Q13new → Income Growth Expectation; Q22new → Labor Search Friction; ec9-12 → Consumption Adjustment Rule

**构造方法**：
1. 将 Q22new 反转为 (1 - Q22new)，使其与 Q13new 方向一致（高值 = 高脆弱性）
2. 对 Q13new + (1-Q22new) 做 PCA，提取第一主成分作为 Fragility Index
3. 如有 LM 数据：加入 ec14, l8 做增强 PCA
4. 标准化到 [0, 1] 区间

**分布对象**：
- 主分布：factor score distribution (PCA第一主成分)
- 经验分布，非参数
- 适合直接用于初始化

**影响的决策模块**：
- Participation block（高脆弱性 → 可能退出劳动市场）
- Search block（高脆弱性 → 预防性搜索强度变化）
- Consumption-smoothing block（高脆弱性 → 增加预防性储蓄）
- Borrowing block（高脆弱性 → 信贷需求增加）


---

### H3: Liquidity Fragility

| 属性 | 值 |
|------|-----|
| **全称** | Liquidity Fragility — 流动性脆弱性 |
| **层级** | 第一圈 MVP |
| **主类别** | 约束（Constraint） |
| **工程类型** | `categorical` (H2M/Buffer/Wealthy) + `dynamic_state` (buffer_months) |
| **时间属性** | 中速状态变量，季度更新（负面冲击可快速恶化） |
| **Agent Container** | `category_states` (liquidity_type) + `dynamic_states` (cash_buffer_months) |

**机制摘要**：流动性不足 → (1) 消费跟随当期收入，(2) 无法承担长期搜索 → 被迫接受次优工作，(3) MPC显著偏高，(4) 负面冲击传导被放大。

**问卷来源**：

| 角色 | 模块 | 题号 | 说明 |
|------|------|------|------|
| 主支持 | Core | Q32 | 是否有储蓄/支票账户 |
| 主支持 | Core | Q33 | 账户余额是否足以覆盖3个月支出 |
| 主支持 | Core | Q47 | 过去12个月是否曾无法按时支付账单 |
| 校准参考 | Informal Work | Q6 | 流动性储蓄可覆盖月数（分布参考） |
| 校准参考 | HH Finance | c1系列 | 储蓄/支票/现金余额（横截面校准） |
| 辅助 | Spending | qsp13new/qsp13a | 收入下降时的调整方式 |

**主加载**：→ Liquidity Fragility
**次加载**：Q32/Q33 → Balance Sheet; qsp13 → Consumption Adjustment Rule

**⚠️ 审计修正**：主干改为 Core Q32+Q33+Q47。HH Finance 和 Informal Work 仅用于分布校准。

**构造方法**：
1. 规则分类：
   - **Hand-to-Mouth**：Q32=No 或 Q33=No 且 Q47=Yes
   - **Adequate Buffer**：Q32=Yes 且 Q33=Yes 且 Q47=No
   - **Wealthy**：Q32=Yes 且 Q33=Yes 且 Q47=No 且高收入分位
2. 参考 Kaplan-Violante (2014) 分类
3. 附加连续状态：buffer_months（从外部分布校准）

**分布对象**：
- 主分布：grouped shares（三类比例）
- 辅助分布：conditional continuous（buffer_months 各类内分布）
- 适合直接用于初始化

**影响的决策模块**：
- Consumption-smoothing block（MPC差异化）
- Search block（搜索持续能力上限）
- Acceptance block（流动性压力压低保留工资）
- Borrowing block（高成本短期借贷需求）

---

### H4: Labor Search Friction

| 属性 | 值 |
|------|-----|
| **全称** | Labor Search Friction — 劳动搜索摩擦 |
| **层级** | 第一圈 MVP（从第二阶段提升） |
| **主类别** | 约束（Constraint）+ 偏好（Preference） |
| **工程类型** | `rule_based` + `dynamic_state` |
| **时间属性** | 中速状态变量，季度更新 |
| **Agent Container** | `behavior_params` (reservation_wage_ratio, flexibility_index) + `dynamic_states` (search_intensity) |

**机制摘要**：(1) 保留工资决定accept/reject → 直接影响失业持续期，(2) 搜索强度决定offer到达率，(3) 灵活性决定搜索空间大小。

**问卷来源**：

| 角色 | 模块 | 题号 | 说明 |
|------|------|------|------|
| 主支持 | LM Quarterly | rw2_reserv_earn | 保留工资 |
| 主支持 | LM Quarterly | js7_search_hours_spent | 每周搜索小时数 |
| 主支持 | LM Quarterly | rw3/rw3b | 搬迁加薪要求 |
| 主支持 | LM Quarterly | rw4/rw4b | 通勤加薪要求 |
| 主支持 | LM Quarterly | rw6/rw6b | 工时加薪要求 |
| 辅助 | LM Quarterly | js6系列 | 搜索渠道 |
| 辅助 | LM Quarterly | js14/js18a/js19 | 申请/面试/offer数 |
| 辅助 | LM Quarterly | js27/js29 | 接受/拒绝原因 |

**主加载**：→ Labor Search Friction
**次加载**：rw2 → Liquidity Fragility; js7 → Labor Fragility

**构造方法**：
1. reservation_wage_ratio = rw2 / 当前或最近工资 → 连续
2. search_intensity = js7 → 连续
3. flexibility_index = PCA(rw3b, rw4b, rw6b) → 因子分数
4. 综合：Search Friction Index = f(上述三者)

**⚠️ 数据频率**：LM Quarterly 为季度，模型月度步进。季度内恒定，季度间线性插值。

**分布对象**：
- reservation_wage_ratio：empirical continuous distribution
- search_intensity：empirical continuous distribution
- flexibility_index：factor score distribution
- 均适合直接用于初始化

**影响的决策模块**：
- Search block（搜索强度 → offer到达率）
- Acceptance block（保留工资 → accept/reject）
- Participation block（极高摩擦 → 可能退出）

---

### H5: Housing Mobility Friction

| 属性 | 值 |
|------|-----|
| **全称** | Housing Mobility Friction — 住房流动性摩擦 |
| **层级** | 第一圈 MVP |
| **主类别** | 状态（State）+ 约束（Constraint） |
| **工程类型** | `categorical` (housing_status) + `conditional_continuous` (ltv_ratio, mobility_score) |
| **时间属性** | 慢变量，年度更新 |
| **Agent Container** | `category_states` (housing_status) + `dynamic_states` (mobility_friction_score) |

**机制摘要**：(1) 自有住房 → 搬迁锁定 → 劳动地理流动性低，(2) 高LTV → 负资产风险 → 被困，(3) 租赁者受租金冲击但搬迁更灵活。

**问卷来源**：

| 角色 | 模块 | 题号 | 说明 |
|------|------|------|------|
| 主支持 | Core | Q41/Q42/Q43 | 拥有/租赁状态、房屋价值 |
| 主支持 | Housing | HQH5系列 | 房贷详细信息（利率/余额/月供/类型） |
| 主支持 | Housing | HQH6系列 | 搬迁意愿和障碍 |
| 辅助 | Housing | HQR系列 | 租赁者租金负担和搬迁意愿 |
| 辅助 | Core | Q43a | 房屋净值 |
| 辅助 | Housing | HQ3a/HQ3b/HQ3c | 房价预期 |

**主加载**：→ Housing Mobility Friction
**次加载**：HQ3 → Inflation Belief; HQH5 → Balance Sheet; HQH6 → Labor Fragility

**构造方法**：
1. 首先分层：Owner vs Renter（Q41）
2. Owner内部：按LTV分层（HQH5余额/Q42价值）
   - Owner-Low-LTV (LTV < 0.6)
   - Owner-High-LTV (LTV >= 0.6)
3. Renter内部：按搬迁灵活性分层（HQR）
   - Renter-Stable
   - Renter-Mobile
4. Mobility Friction Score = f(HQH6搬迁障碍, 住房锁定程度)

**分布对象**：
- housing_status：grouped shares（四类比例）
- ltv_ratio（仅Owner）：conditional continuous distribution
- mobility_friction_score：conditional continuous distribution
- 适合直接用于初始化

**影响的决策模块**：
- Search block（地理搜索范围约束）
- Participation block（搬迁摩擦 → 本地市场锁定）
- Consumption-smoothing block（房贷支付 vs 租金 → 固定支出差异）

---

### H6: Consumption Adjustment Rule

| 属性 | 值 |
|------|-----|
| **全称** | Consumption Adjustment Rule — 消费调整规则异质性 |
| **层级** | 第一圈 MVP |
| **主类别** | 调整规则（Adjustment Rule） |
| **工程类型** | `rule_based` |
| **时间属性** | 慢变量（偏好属性，基本不变） |
| **Agent Container** | `behavior_params` |

**机制摘要**：(1) 正面冲击MPC决定储蓄vs消费分配，(2) 负面冲击MPC决定缓冲策略，(3) 不对称性反映损失厌恶，(4) 影响总需求→就业反馈环路。

**问卷来源**：

| 角色 | 模块 | 题号 | 说明 |
|------|------|------|------|
| 主支持 | Spending | qsp12n | 收入增加10%时，增加消费占比 |
| 主支持 | Spending | qsp13new | 收入减少10%时，减少消费占比 |
| 辅助 | Spending | qsp12a_1~3 | 增加消费的具体分配 |
| 辅助 | Spending | qsp13a_1~3 | 减少消费的具体分配 |
| 辅助 | Spending | qsp3/qsp4/qsp5 | 消费支出结构 |
| 辅助 | Core | Q26v2 | 预期支出变化 |
| 辅助 | Spending | k2e/k2f | 计划行为和自我控制 |

**主加载**：→ Consumption Adjustment Rule
**次加载**：qsp12n → Liquidity Fragility（高MPC反映约束）; qsp3/qsp4 → Balance Sheet

**构造方法**：
1. mpc_positive = qsp12n / 100（正向MPC，0-1）
2. mpc_negative = qsp13new / 100（负向MPC，0-1）
3. asymmetry_ratio = mpc_negative / mpc_positive（损失厌恶指标）
4. Latent class 分类：
   - **Saver**：mpc_positive 低（增收主要储蓄）+ mpc_negative 低（减收靠缓冲）
   - **Spender**：mpc_positive 高 + mpc_negative 高（消费跟随收入）
   - **Smoother**：两者中等（跨期平滑）

**分布对象**：
- mpc_positive / mpc_negative：empirical continuous distribution
- asymmetry_ratio：empirical continuous distribution
- consumption_type (Saver/Spender/Smoother)：latent class probabilities
- 均适合直接用于初始化

**影响的决策模块**：
- Consumption-smoothing block（核心参数：MPC决定消费响应）
- Borrowing block（Spender在负冲击下可能触发借贷）
- Search block（间接：高MPC → 失业冲击影响更大 → 搜索更紧迫）

---

## 第二圈：扩展系统（4 维）

---

### H7: Inflation Belief Heterogeneity

| 属性 | 值 |
|------|-----|
| **全称** | Inflation Belief Heterogeneity — 通胀预期分歧 |
| **层级** | 第二圈 扩展（从MVP降级） |
| **工程类型** | `dynamic_state` (continuous) |
| **时间属性** | 快速预期变量，月度更新 |
| **Agent Container** | `dynamic_states` |
| **引入时机** | 阶段4+，加入工资谈判/价格设定模块时引入 |

**问卷来源**：Core Q9系列（密度预测）、Q8v2（感知过去通胀）
**构造方法**：Q9_cent50（中位数预期）+ Q9_iqr（不确定性）
**分布对象**：empirical continuous distribution（二维联合）

### H8: Credit Access Constraint

| 属性 | 值 |
|------|-----|
| **全称** | Credit Access Constraint — 信贷可得性约束 |
| **层级** | 第二圈 扩展 |
| **工程类型** | `categorical` + `dynamic_state` |
| **时间属性** | 中速状态变量 |
| **Agent Container** | `category_states` + `dynamic_states` |
| **引入时机** | 阶段4+，扩展 borrowing block 时引入 |

**问卷来源**：Credit Access N1-N11
**构造方法**：Credit Access Index = PCA(持有广度, 被拒经历, discouraged标记, 预期审批概率)
**分布对象**：factor score distribution → 分类(Unconstrained/Partial/Severe/Discouraged)
**特别注意**：N11 (discouraged borrower) 应在扩展时建模为内生决策节点

### H9: Numeracy & Planning

| 属性 | 值 |
|------|-----|
| **全称** | Numeracy & Planning Capability |
| **层级** | 第二圈 扩展 |
| **工程类型** | `continuous` (static) |
| **时间属性** | 慢变量（成人后不变） |
| **Agent Container** | `static_traits` |
| **引入时机** | 阶段4+，需要建模预期形成质量差异时引入 |

**问卷来源**：Core QNUM1-9
**构造方法**：正确数加总（0-7分）
**分布对象**：empirical discrete distribution
**MVP替代**：教育水平(Q36)作为粗糙代理

### H10: Risk Preference

| 属性 | 值 |
|------|-----|
| **全称** | Risk Preference — 风险偏好异质性 |
| **层级** | 第二圈 扩展 |
| **工程类型** | `continuous` (static) |
| **时间属性** | 慢变量 |
| **Agent Container** | `static_traits` |
| **引入时机** | 阶段4+，需要建模资产组合或自雇选择时引入 |

**问卷来源**：Core QRA1/QRA2
**构造方法**：QRA1直接使用（1-10标度）或 QRA1×QRA2 二维
**分布对象**：empirical continuous distribution

---

## 第三圈：校准 / 验证层（2+1 维）

---

### H11: Balance Sheet Composition

| 属性 | 值 |
|------|-----|
| **全称** | Balance Sheet Composition — 家庭资产负债表结构 |
| **层级** | 第三圈 校准/验证 |
| **工程类型** | `conditional_continuous` (slow state vector) |
| **时间属性** | 慢变量，年度变化 |
| **用途** | 仅用于初始人口财富分布校准和横截面验证 |

**问卷来源**：HH Finance c1-c9（金融资产）、d2-d10（负债）、Core Q35（资产持有类型）
**构造方法**：net_worth = 总资产 - 总负债；资产结构比 liquid/illiquid
**分布对象**：conditional continuous distribution (net worth quintile + 结构标记)
**限制**：HH Finance 仅 2014-2019，已停更。不可用于动态更新。Core Q35（月度）可作简化替代。

### H12: Policy Sensitivity

| 属性 | 值 |
|------|-----|
| **全称** | Policy Sensitivity — 政策敏感度 |
| **层级** | 第三圈 校准/验证 |
| **工程类型** | `conditional_continuous` (slow/fast parameter) |
| **时间属性** | 快速预期变量（对政治事件敏感），但更新依赖 Policy Survey 频率 |
| **用途** | 仅用于政策冲击情景分析 |

**问卷来源**：Policy Survey qp1x系列、qp2_1~20
**构造方法**：20项政策 PCA 降维 → 2-3 因子
**分布对象**：factor score distribution
**注意**：partisan bias 严重，直接使用需谨慎

### Informal Work（分布参考）

| 属性 | 值 |
|------|-----|
| **全称** | Informal Work / Side Work Exposure |
| **层级** | 分布参考（非个体级数据源） |
| **用途** | 仅用于 Liquidity Fragility 中 buffer_months 分布的外部校准 |

**问卷来源**：波士顿联储 SIWP Informal Work Q6
**说明**：来自不同调查系统，样本不可与 FRBNY SCE 个体级匹配。仅提供"流动性储蓄可覆盖月数"的分布形状参考。

---

## 工程类型重标注总表

| # | 异质性 | 工程类型 | 初始建议 | 审计后调整 | 理由 |
|---|--------|---------|---------|-----------|------|
| H1 | Income Growth Expectation | `dynamic_state` (continuous) | dynamic continuous | ✅ 一致 | — |
| H2 | Labor Fragility | `dynamic_state` (continuous index) | dynamic continuous index | ✅ 一致 | — |
| H3 | Liquidity Fragility | `categorical` + `dynamic_state` | categorical + dynamic buffer | ✅ 一致 | — |
| H4 | Labor Search Friction | `rule_based` + `dynamic_state` | rule-based + dynamic state | ✅ 一致 | — |
| H5 | Housing Mobility Friction | `categorical` + `conditional_continuous` | categorical + conditional continuous | ✅ 一致 | — |
| H6 | Consumption Adjustment Rule | `rule_based` | rule-based | ✅ 一致 | — |
| H7 | Inflation Belief | `dynamic_state` (continuous) | dynamic continuous | ✅ 一致 | — |
| H8 | Credit Access Constraint | `categorical` + `dynamic_state` | categorical / dynamic constraint | 微调：加`categorical` | 分类(Un/Partial/Severe/Discouraged)更符合数据 |
| H9 | Numeracy & Planning | `continuous` (static) | static continuous | ✅ 一致 | — |
| H10 | Risk Preference | `continuous` (static) | static continuous | ✅ 一致 | — |
| H11 | Balance Sheet Composition | `conditional_continuous` (slow) | slow state vector | 微调：改为conditional | 净财富连续，但仅在有数据时有意义 |
| H12 | Policy Sensitivity | `conditional_continuous` | slow/fast parameter | 微调：改为conditional | 因子分数连续，但依赖 Policy Survey 可用性 |