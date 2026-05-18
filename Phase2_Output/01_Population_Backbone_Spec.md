# Population Backbone Spec

> 版本：v1.0 | 阶段：Phase 2 — Population Initialization

---

## 一、骨架变量定义

| 字段 | 矩阵 | 列 | dtype | 取值 | 来源 | 说明 |
|------|------|---|-------|------|------|------|
| age | static_traits | 0 | int16 | 18-85 | CPS/SCE _AGE_CAT | 按三档比例展开为连续年龄 |
| education | static_traits | 1 | int8 | 0-2 | SCE _EDU_CAT | 0=HS, 1=SomeCollege, 2=College+ |
| marital_status | static_traits | 2 | int8 | 0-1 | LMQ married | 0=unmarried, 1=married |
| household_size | static_traits | 3 | int8 | 1-8 | LMQ hhsize | 家庭人数 |

## 二、经验分布参数（从数据提取）

### Age（按 SCE _AGE_CAT 分布展开）

| 分组 | 比例 | 年龄范围 | 展开方式 |
|------|------|---------|---------|
| Under 40 | 27.7% | 18-39 | 均匀分布 |
| 40 to 60 | 39.1% | 40-60 | 均匀分布 |
| Over 60 | 33.2% | 61-85 | 均匀分布 |

### Education

| 分组 | 比例 | 编码 |
|------|------|------|
| High School or less | 11.4% | 0 |
| Some College | 33.2% | 1 |
| College+ | 55.4% | 2 |

### Employment State（核心分类状态，非骨架但必须优先生成）

从 BLS 官方数据校准（SCE 样本 E/U/N=56/13/31% 不代表真实美国劳动力市场）：

| 状态 | BLS 近似比例 | 编码 | 说明 |
|------|-------------|------|------|
| Employed (E) | 60% | 0 | 包含全职+兼职 |
| Unemployed (U) | 4% | 1 | 积极搜索 |
| Not in LF (N) | 36% | 2 | 退休、学生、家庭照护等 |

**注意**：BLS 比例应按 age × education 条件化。年轻人失业率更高，老年人 NILF 比例更高。

### Housing Status

从 LMQ own_rent 分布（经美国人口普查校准）：

| 状态 | 比例 | 编码 | 说明 |
|------|------|------|------|
| Renter-Mobile | 12% | 0 | 租赁且灵活 |
| Renter-Stable | 20% | 1 | 租赁但锁定 |
| Owner-Low-LTV | 45% | 2 | 自有低杠杆 |
| Owner-High-LTV | 23% | 3 | 自有高杠杆 |

**说明**：LMQ 数据 own=73%, rent=25%。美国整体 homeownership rate 约 66%（Census）。这里使用 Census 校准值 owner:renter ≈ 66:34，再按 LTV 和 mobility 内部比例拆分。

### Liquidity Type

从 Core Q33 分布 + Kaplan-Violante 参考：

| 类型 | 比例 | 编码 | 说明 |
|------|------|------|------|
| Hand-to-Mouth (H2M) | 30% | 0 | Q33=No 且低收入 |
| Adequate Buffer | 45% | 1 | Q33=Yes 但非高净值 |
| Wealthy | 25% | 2 | Q33=Yes 且高收入 |

**说明**：Q33 显示约 51% 无法覆盖 3 个月支出。结合 Kaplan-Violante (2014) 美国 H2M 约 30-33% 的估计做校准。

### Consumption Type

从 Spending qsp12n × qsp13new 联合分布推断：

| 类型 | 比例 | 编码 | 说明 |
|------|------|------|------|
| Saver | 30% | 0 | qsp12n 低（增收主储蓄） |
| Smoother | 40% | 1 | 两者中等 |
| Spender | 30% | 2 | qsp12n 高（增收主消费） |

## 三、骨架生成顺序

```
1. age ← 按三档比例 + 档内均匀分布
2. education ← 按三类比例（条件于 age 档）
3. marital_status ← 按比例（条件于 age）
4. household_size ← 按分布（条件于 marital_status）
5. employment_state ← 按 BLS 比例（条件于 age × education）
6. housing_status ← 按比例（条件于 age × income_proxy）
7. liquidity_type ← 按比例（条件于 employment × housing）
8. consumption_type ← 按比例（条件于 liquidity_type）
```

**关键**：步骤 1-4 是 static_traits，步骤 5-8 是 category_states。后者依赖前者。
