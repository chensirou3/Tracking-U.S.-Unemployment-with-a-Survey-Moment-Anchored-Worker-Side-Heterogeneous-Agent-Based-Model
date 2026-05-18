# 文档 4：Survey-to-Agent 映射表

> 版本：v1.0
> 阶段：Phase 1 — Heterogeneity Audit & Engineering

---

## 一、映射总表（MVP 6 维）

### 表 4a：问卷题项 → 异质性维度 映射

| 问卷模块 | 题号 | 题目简述 | 主加载异质性 | 次加载异质性 |
|---------|------|---------|-------------|-------------|
| Core | Q24_cent50 | 1年期收入增长预期中位数 | H1 Income Growth Exp | — |
| Core | Q24_iqr | 1年期收入增长预期IQR | H1 Income Growth Exp | — |
| Core | Q25v2 | 预期收入变化方向 | H1 Income Growth Exp | — |
| Core | Q4new | 过去12个月家庭总收入 | H1 Income Growth Exp | H11 Balance Sheet |
| Core | Q28/Q29 | 主观财务状况评估 | H1 Income Growth Exp | H3 Liquidity Fragility |
| Core | Q30new | 预期未来财务状况 | H1 Income Growth Exp | — |
| Core | Q13new | 未来12月失去工作概率 | H2 Labor Fragility | H1 Income Growth Exp |
| Core | Q22new | 失业后4月内再就业概率 | H2 Labor Fragility | H4 Labor Search Friction |
| Core | Q15/Q16 | 自愿离职概率 | H2 Labor Fragility | — |
| LM | ec14 | 被裁概率 | H2 Labor Fragility | — |
| LM | l8 | 无工作月数 | H2 Labor Fragility | — |
| LM | ec9-12 | 工资/福利/技能/晋升满意度 | H2 Labor Fragility | H6 Consumption Adj |
| Core | Q32 | 是否有储蓄/支票账户 | H3 Liquidity Fragility | H11 Balance Sheet |
| Core | Q33 | 账户余额≥3个月支出 | H3 Liquidity Fragility | H11 Balance Sheet |
| Core | Q47 | 过去12月无法按时付账 | H3 Liquidity Fragility | — |
| LM Quarterly | rw2 | 保留工资 | H4 Labor Search Friction | H3 Liquidity Fragility |
| LM Quarterly | js7 | 每周搜索小时数 | H4 Labor Search Friction | H2 Labor Fragility |
| LM Quarterly | rw3/rw3b | 搬迁加薪要求 | H4 Labor Search Friction | — |
| LM Quarterly | rw4/rw4b | 通勤加薪要求 | H4 Labor Search Friction | — |
| LM Quarterly | rw6/rw6b | 工时加薪要求 | H4 Labor Search Friction | — |
| LM Quarterly | js14/js18a/js19 | 申请/面试/offer数 | H4 Labor Search Friction | — |
| Core | Q41 | 住房拥有/租赁状态 | H5 Housing Mobility | — |
| Core | Q42/Q43 | 房屋价值/净值 | H5 Housing Mobility | H11 Balance Sheet |
| Housing | HQH5系列 | 房贷详细信息 | H5 Housing Mobility | H11 Balance Sheet |
| Housing | HQH6系列 | 搬迁意愿和障碍 | H5 Housing Mobility | H2 Labor Fragility |
| Housing | HQR系列 | 租赁者租金负担/搬迁 | H5 Housing Mobility | — |
| Spending | qsp12n | 收入+10%时消费增加占比 | H6 Consumption Adj | H3 Liquidity Fragility |
| Spending | qsp13new | 收入-10%时消费减少占比 | H6 Consumption Adj | H3 Liquidity Fragility |
| Spending | qsp12a_1~3 | 增加消费的分配 | H6 Consumption Adj | — |
| Spending | qsp13a_1~3 | 减少消费的分配 | H6 Consumption Adj | — |

---

### 表 4b：异质性维度 → Agent Container 映射

| 异质性 | Agent Container | 字段名 | 初始化方法 | 更新频率 | 影响的决策模块 |
|--------|----------------|--------|-----------|---------|---------------|
| H1 Income Growth Exp | dynamic_states | income_expectation | Q24_cent50 经验分布抽样 | 月度 | Consumption, Search, Acceptance, Participation |
| H1 Income Growth Exp | dynamic_states | income_uncertainty | Q24_iqr 经验分布抽样 | 月度 | Consumption, Search |
| H2 Labor Fragility | dynamic_states | labor_fragility | PCA(Q13new, 1-Q22new) 因子分数抽样 | 季度 | Participation, Search, Consumption, Borrowing |
| H3 Liquidity Frag | category_states | liquidity_type | 规则分类(Q32,Q33,Q47) 按比例赋值 | 季度（冲击时即时） | Consumption, Search, Acceptance, Borrowing |
| H3 Liquidity Frag | dynamic_states | cash_buffer_months | Informal Work Q6 分布校准 → 条件抽样 | 季度（冲击时即时） | Search, Borrowing |
| H4 Labor Search | behavior_params | reservation_wage_ratio | rw2/wage 经验分布抽样 | 季度 | Acceptance |
| H4 Labor Search | dynamic_states | search_intensity | js7 经验分布抽样 | 季度 | Search |
| H4 Labor Search | behavior_params | flexibility_index | PCA(rw3b,rw4b,rw6b) 因子分数抽样 | 年度 | Search |
| H5 Housing Mobility | category_states | housing_status | 按Q41+LTV规则分类比例赋值 | 年度 | Search, Participation, Consumption |
| H5 Housing Mobility | dynamic_states | mobility_friction_score | HQH6 构造分数 条件抽样 | 年度 | Search, Participation |
| H6 Consumption Adj | behavior_params | mpc_positive | qsp12n/100 经验分布抽样 | 不更新（慢偏好） | Consumption |
| H6 Consumption Adj | behavior_params | mpc_negative | qsp13new/100 经验分布抽样 | 不更新（慢偏好） | Consumption |
| H6 Consumption Adj | behavior_params | asymmetry_ratio | mpc_negative/mpc_positive 派生 | 不更新（慢偏好） | Consumption |
| H6 Consumption Adj | category_states | consumption_type | latent class(Saver/Spender/Smoother) 按概率赋值 | 不更新（慢偏好） | Consumption, Borrowing |

---

### 表 4c：人口学背景变量（非异质性维度，但 agent 必需）

| 字段 | Agent Container | 来源 | 初始化 | 更新 | 说明 |
|------|----------------|------|--------|------|------|
| age | static_traits | Core Q36 | 按人口分布抽样 | 年度+1 | 年龄 |
| education | static_traits | Core Q36 | 按教育分布抽样 | 不更新 | 教育水平（MVP阶段代理Numeracy） |
| marital_status | static_traits | Core Q38 | 按分布抽样 | 不更新 | 婚姻状况 |
| household_size | static_traits | Core Q39 | 按分布抽样 | 不更新 | 家庭规模 |
| household_income | dynamic_states | Core Q4new | 按分布抽样 | 月度 | 家庭收入（受就业状态影响） |
| employment_state | category_states | Core Q10/Q10a | 按E/U/N比例赋值 | 月度 | 就业状态（E=就业/U=失业/N=非劳动力） |
| unemployment_duration | dynamic_states | LM l8 | 条件抽样（仅U状态） | 月度+1 | 失业持续月数 |

---

## 二、交叉加载关系图

```
问卷题项                 主加载                    次加载
─────────────────────────────────────────────────────────────
Q13new ──────────────→ H2 Labor Fragility ──→ H1 Income Growth
Q22new ──────────────→ H2 Labor Fragility ──→ H4 Search Friction
Q28/Q29 ─────────────→ H1 Income Growth ───→ H3 Liquidity
Q32/Q33 ─────────────→ H3 Liquidity ────────→ H11 Balance Sheet
rw2 (保留工资) ──────→ H4 Search Friction ─→ H3 Liquidity
js7 (搜索小时) ──────→ H4 Search Friction ─→ H2 Labor Fragility
qsp12n/qsp13new ─────→ H6 Consumption Adj ─→ H3 Liquidity
HQH6 (搬迁障碍) ────→ H5 Housing Mobility ─→ H2 Labor Fragility
ec9-12 (满意度) ─────→ H2 Labor Fragility ─→ H6 Consumption Adj
```

---

## 三、数据可用性约束汇总

| 数据来源 | 频率 | 覆盖期 | 可用性 | 在本项目中的角色 |
|---------|------|--------|--------|----------------|
| Core Survey Microdata | 月度 | 2013-present | ✅ 主干 | 动态系统主数据源 |
| LM Survey Microdata | 季度 | 2013-2021 | ✅ 可用 | H4搜索摩擦主源；H2增强 |
| LM Quarterly Microdata | 季度 | 2013-2021 | ✅ 可用 | 保留工资、搜索强度 |
| Housing Survey | 年度 | 2014-present | ✅ 可用 | H5住房状态主源 |
| Household Spending | 年度 | 2015-present | ✅ 可用 | H6消费规则主源 |
| HH Finance | 季度 | 2014-2019 | ⚠️ 已停更 | 仅横截面校准 |
| Credit Access | 年度 | 2013-present | ✅ 可用 | H8扩展阶段 |
| Policy Survey | 不定期 | 2015-present | ✅ 可用 | H12校准阶段 |
| Informal Work | 一次性 | 2015 | ⚠️ 不同调查 | 仅分布参考 |
