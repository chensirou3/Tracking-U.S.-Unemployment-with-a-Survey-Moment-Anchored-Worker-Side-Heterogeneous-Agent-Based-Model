# Simulation Order Specification

> Phase 3 — Main Model Core Engine

## 月度执行顺序

每月 t 执行以下步骤，顺序固定不可更改：

```
Step  1: env = environment.get(t)                    # 读取外部环境
Step  2: update_expectations(cs, ds, env)             # 更新预期状态（快变量）
Step  3: exit_to_n, enter_from_n = participation()    # 参与决策
Step  4: search_intensity = search()                  # 搜索强度更新
Step  5: has_offer, wage, separated = opportunity()   # offer到达 + 裁员
Step  6: accepts = acceptance()                       # 接受/拒绝
Step  7: transitions = update_labor_states()          # 劳动状态转移
Step  8: update_income()                              # 收入更新
Step  9: consumption, savings = consumption()         # 消费调整
Step 10: buffer, liq, debt = borrowing()              # 流动性更新
Step 11: aggregates = aggregate()                     # 聚合输出
```

## 步骤依赖关系

| 步骤 | 依赖于 | 修改的矩阵/列 |
|------|--------|-------------|
| 2 | env | dynamic_states: income_exp, income_unc, labor_frag |
| 3 | cs, ds, st, env | (输出 masks，不直接写矩阵) |
| 4 | cs, ds, bp, env | dynamic_states: search_intensity |
| 5 | cs, ds, bp, env | (输出 masks + offered_wage) |
| 6 | cs, ds, bp, has_offer | (输出 accepts mask) |
| 7 | masks from 3,5,6 | category_states: employment; dynamic_states: unemp_dur, search_int |
| 8 | cs, ds, st, env | dynamic_states: household_income |
| 9 | cs, ds, bp, env, prev_income | (输出 consumption, savings) |
| 10 | cs, ds, savings, env | dynamic_states: cash_buffer, debt_stress; category_states: liquidity_type |
| 11 | cs, ds, bp, transitions | (只读，不写矩阵) |

## 关键约束

- 步骤 3-6（劳动 4 block）必须在步骤 7（状态转移）之前执行
- 步骤 8（收入更新）必须在步骤 7 之后（因为收入取决于新就业状态）
- 步骤 9-10（消费/借贷）必须在步骤 8 之后
- 步骤 11（聚合）必须在所有更新之后
