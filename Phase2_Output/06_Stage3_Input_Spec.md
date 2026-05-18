# Stage 3 Input Specification

> 版本：v1.0 | 从 Phase 2 Population Initialization 输出

---

## 一、文件清单

| 文件 | 路径 | 说明 |
|------|------|------|
| 人口数据 | `Phase2_Output/population_v1.npz` | 4 个矩阵，100,000 agents |
| 矩阵映射 | `Phase2_Output/matrix_schema_map.json` | 列索引 → 变量名映射 |
| 本文档 | `Phase2_Output/06_Stage3_Input_Spec.md` | 读取和使用规范 |

## 二、读取方式

```python
import numpy as np
import json

# 加载人口
pop = np.load('Phase2_Output/population_v1.npz')
static_traits    = pop['static_traits']      # (N, 4) int16
category_states  = pop['category_states']     # (N, 4) int8
dynamic_states   = pop['dynamic_states']      # (N, 9) float64
behavior_params  = pop['behavior_params']     # (N, 5) float64

# 加载映射
with open('Phase2_Output/matrix_schema_map.json') as f:
    schema = json.load(f)
```

## 三、各矩阵字段详情

### static_traits (N, 4) — 基本不更新

| Col | 字段 | dtype | 范围 | 更新 | 用途 |
|-----|------|-------|------|------|------|
| 0 | age | int16 | 18-85 | 年度+1 | 条件分组 |
| 1 | education | int16 | 0-2 | 不更新 | 0=HS,1=SomeCol,2=College+ |
| 2 | marital_status | int16 | 0-1 | 不更新 | 0=single,1=married |
| 3 | household_size | int16 | 1-6 | 不更新 | 家庭人数 |

### category_states (N, 4) — 状态转移

| Col | 字段 | dtype | 编码 | 更新频率 | 用途 |
|-----|------|-------|------|---------|------|
| 0 | employment_state | int8 | 0=E,1=U,2=N | **月度**（核心状态转移） | Search/Acceptance/Participation block |
| 1 | liquidity_type | int8 | 0=H2M,1=Buffer,2=Wealthy | 季度（冲击即时） | Consumption/Borrowing block |
| 2 | housing_status | int8 | 0=RentMob,1=RentStb,2=OwnLow,3=OwnHigh | 年度 | Search/Consumption block |
| 3 | consumption_type | int8 | 0=Saver,1=Smoother,2=Spender | 底层不变 | Consumption block |

### dynamic_states (N, 9) — 每期更新

| Col | 字段 | dtype | 范围 | 更新频率 | 决策 Block |
|-----|------|-------|------|---------|-----------|
| 0 | income_expectation | float64 | [-0.30, 0.50] | 月度 | Consumption, Search, Acceptance |
| 1 | income_uncertainty | float64 | [0, 0.50] | 月度 | Consumption, Search |
| 2 | labor_fragility | float64 | [0, 1] | 季度 | Participation, Search, Consumption |
| 3 | cash_buffer_months | float64 | [0, 36] | 季度/冲击 | Search, Borrowing |
| 4 | search_intensity | float64 | [0, 40] | 季度 | Search block（仅U状态） |
| 5 | mobility_friction_score | float64 | [0, 1] | 年度 | Search block |
| 6 | household_income | float64 | [5, 500] $k | 月度 | 全局 |
| 7 | unemployment_duration | float64 | [0, 60] months | 月度（U+1） | Acceptance block |
| 8 | debt_stress | float64 | [0, 1] | 季度 | Borrowing block |

### behavior_params (N, 5) — 慢参数

| Col | 字段 | dtype | 范围 | 更新频率 | 决策 Block |
|-----|------|-------|------|---------|-----------|
| 0 | mpc_positive | float64 | (0, 1) | 底层不变；有效值随状态调节 | Consumption block |
| 1 | mpc_negative | float64 | (0, 1) | 同上 | Consumption block |
| 2 | asymmetry_ratio | float64 | (0, ∞) | 同上 | Consumption block |
| 3 | reservation_wage_ratio | float64 | [0.5, 5.0] | 季度（随失业持续期递减） | Acceptance block |
| 4 | flexibility_index | float64 | [-3, 3] | 年度 | Search block |

## 四、阶段 3 决策 Block 与变量映射

| 决策 Block | 输入变量 | 输出 |
|-----------|---------|------|
| **Search** | employment_state, search_intensity, flexibility_index, mobility_friction_score | offer_arrival (0/1) |
| **Acceptance** | reservation_wage_ratio, unemployment_duration, income_expectation, liquidity_type | accept/reject |
| **Participation** | labor_fragility, income_expectation, age, cash_buffer_months | E/U/N 转移 |
| **Consumption** | mpc_positive, mpc_negative, consumption_type, liquidity_type, household_income | consumption, savings |
| **Borrowing** | debt_stress, cash_buffer_months, liquidity_type | borrow/repay |

## 五、关键约束提醒

1. **employment_state 是核心状态变量**：每步必须先更新 employment，再由新 employment 驱动其他字段更新
2. **search_intensity 仅 U 状态有效**：E 和 N 状态的 agent 此字段必须为 0
3. **unemployment_duration 仅 U 状态递增**：转为 E 或 N 时归零
4. **有效 MPC ≠ 底层 MPC**：阶段 3 必须实现 `effective_mpc = base_mpc × f(liquidity_type, employment_state)`
5. **reservation_wage_ratio 随失业持续期递减**：建议 `rw_t = rw_0 × exp(-decay × duration)`
6. **cash_buffer_months 逐月消耗**：U 状态且无收入时每月减 1（简化）

## 六、验证状态

| 检查项 | 状态 |
|--------|------|
| 所有字段无 NaN | ✅ |
| 所有字段在合法范围内 | ✅ |
| 5 对联合关系方向正确 | ✅ |
| 边际分布与目标对齐 | ✅ |
| 10k/50k/100k 规模稳定 | ✅ |
| 不同 seed 结果一致 | ✅ (CV < 1%) |
| **阶段 3 可直接读取并开始** | ✅ |
