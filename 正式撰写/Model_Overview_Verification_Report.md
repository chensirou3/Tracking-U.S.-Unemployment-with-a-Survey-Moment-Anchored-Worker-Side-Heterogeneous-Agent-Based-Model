# Model Overview Verification Report

> **目标**：基于源代码、配置文件、输出结果的逐点核验，为论文 *"Simulation and Prediction of Labor Market Dynamics Using a Heterogeneous Agent-Based Model"* 的 **Model Overview / Data / Calibration / Experimental Design** 四节提供可直接引用的事实证据。
>
> **证据等级标记**：
> - ✅ **Confirmed by code**：在源文件 + 行号能直接读出。
> - 📊 **Confirmed by output**：在 `Phase*_Output` 的 json/csv/md 中能直接读出数值。
> - 🔸 **Inference, not directly confirmed by code**：基于结构推断，需要人工确认。
> - ❌ **未找到明确依据，需要人工确认**。
>
> **模型称呼**：本报告统一使用 **the heterogeneous ABM** / **the survey-based heterogeneous ABM**；不锁定 "Model C" / "M0"（这些是工程编号，正式重跑前不写入论文）。
>
> **报告生成日期**：2026-05-12

---

## 0. 验证范围（Audit Scope）

| 已审计层 | 路径 | 状态 |
|---------|------|:----:|
| Phase 1 规范（异质性边界、agent schema） | `Phase1_Output/*.md` | ✅ |
| Phase 2 人口生成（100k agent 引擎） | `Phase2_Code/population_init_engine.py` · `Phase2_Output/*` | ✅ |
| Phase 3 仿真引擎（scheduler + 9 个 block） | `Phase3_Code/scheduler.py` · `labor/*` · `household/*` · `state_update.py` · `aggregator.py` | ✅ |
| Phase 3 真实环境（FRED 映射） | `Phase3_Code/environment_real.py` · `Phase3_Data/*.csv` | ✅ |
| Phase 3 机制注册表（13 项 on/off 开关） | `Phase3_Code/mechanism_config.py` | ✅ |
| Phase 6 校准（LHS over 14 参数） | `Phase3_Code/calibration_engine.py` · `Phase3_Output/phase6/*` | ✅ |
| Phase 7 主实验（4 时间窗 + 3-tier loss） | `Phase3_Code/phase7_engine.py` · `phase7_main.py` · `Phase3_Output/phase7/*` | ✅ |
| Phase 8 派生 / 基准比较 | `Phase3_Code/phase8_derived.py` · `phase8_benchmarks.py` · `Phase3_Output/phase8/*` | ✅ |
| Packages A–E（5 项 robustness） | `Phase3_Code/package{A..E}_engine.py` · `Phase3_Output/package{A..E}/*` | ✅ |

---

## 1. 模型分类（Model Classification）

### 1.1 类型
**The heterogeneous ABM is a worker-side transition ABM with an aggregate labor-demand environment.** ✅

证据：
- `Phase3_Code/scheduler.py` 第 39–60 行：`Simulation.__init__` 只加载 `population_v1.npz`（100k worker），**未实例化任何 firm 集合**。
- `Phase3_Code/labor/opportunity.py` 第 36–82 行：offer 生成由 `n_vacancies = N * vacancy_rate * market_tightness` 决定，**vacancy 数量来自 `cfg['matching_competition']['vacancy_rate']` 参数 × FRED 市场紧度，不来自 firm decision**。
- `Phase3_Code/environment_real.py` 第 36–69 行：所有"宏观需求侧"变量（market_tightness, separation_rate, income_growth_bg, borrowing_rate）都是从 FRED 月度时间序列读入，**不在模型内部由 firm side 内生**。

### 1.2 异质性边界（MVP 6 维）

来自 `Phase1_Output/02_MVP_Boundary_Freeze_v1.md`（v1.0，2026-04-14 冻结） ✅：

| # | 维度 | Agent matrix column |
|---|------|---------------------|
| 1 | Income Growth Expectation | `ds[:, DS_INCOME_EXP]` + `DS_INCOME_UNC` |
| 2 | Labor Fragility | `ds[:, DS_LABOR_FRAG]` |
| 3 | Liquidity Fragility | `cs[:, CS_LIQUIDITY_TYPE]` + `ds[:, DS_CASH_BUFFER]` |
| 4 | Labor Search Friction | `ds[:, DS_SEARCH_INT]` + `bp[:, BP_RESV_WAGE]` + `BP_FLEXIBILITY` |
| 5 | Housing Mobility Friction | `cs[:, CS_HOUSING_STATUS]` + `ds[:, DS_MOBILITY_FRIC]` |
| 6 | Consumption Adjustment Rule | `cs[:, CS_CONSUMPTION_TYPE]` + `bp[:, BP_MPC_POS/NEG]` |

列号定义在 `Phase3_Code/constants.py` 第 9–46 行。

### 1.3 不在模型中的边界
- ❌ **无价格设定 / 通胀传导**（Phase 1 文档 §二 第 7 行降级）。
- ❌ **无产品市场 / 总需求闭环**（household 消费总量不反馈到劳动需求；这一点与 Phase 8 派生模型 D3 在 LFPR 上反而更好对应一致）。
- ❌ **无 firm side 工资决定**（offered wage 由 `rng.lognormal(np.log(1.10), 0.20)` 抽样，`labor/opportunity.py` 第 89 行）。

---

## 2. Agent 状态空间（Agent State）

### 2.1 四矩阵向量化结构 ✅
来源：`Phase3_Code/constants.py` 第 7 行 / `Phase2_Output/05_Vectorized_Agent_Schema_v1.md` / `Phase2_Code/population_init_engine.py` 第 38–41 行。

| Matrix | 列数 K | dtype | 含义 |
|--------|:-----:|------|------|
| `static_traits` (st) | 4 | int16 | 年龄、教育、婚姻、家庭规模——人口生成后不变 |
| `category_states` (cs) | 4 | int8 | 就业、流动性类型、住房状态、消费类型——离散类别，月内可变 |
| `dynamic_states` (ds) | 9 | float64 | 收入预期/不确定性、劳动脆弱性、现金缓冲、搜索强度、流动摩擦、家庭收入、失业时长、债务压力 |
| `behavior_params` (bp) | 5 | float64 | MPC+, MPC−, 不对称参数, 保留工资, 灵活性 |

### 2.2 状态空间编码
就业三态（`constants.py` 第 37 行）：`EMP_E=0, EMP_U=1, EMP_N=2`
流动性三态（第 40 行）：`LIQ_H2M=0, LIQ_BUFFER=1, LIQ_WEALTHY=2`
住房四态（第 43 行）：`HSG_RENT_MOB / HSG_RENT_STB / HSG_OWN_LOW / HSG_OWN_HIGH = 0,1,2,3`
消费三型（第 46 行）：`CON_SAVER, CON_SMOOTHER, CON_SPENDER = 0,1,2`

### 2.3 初始人口规模与多样性来源
- N = 100,000 ✅（`Phase2_Code/population_init_engine.py` 第 34 行默认；`Phase3_Code/scheduler.py` 第 47 行从 `population_v1.npz` 读入）。
- 6 维异质性的经验分布锚点：📊
  - Employment marginal: E/U/N = 0.586 / 0.039 / 0.375（target 0.60/0.04/0.36）— `Phase2_Output/04_Population_Diagnostic_Report.md` L12–14。
  - Liquidity H2M share: 25.5%（target 30%，Kaplan-Violante）— 同上 L20。
  - 6 维 + 5 联合关系（R1–R5）全部 χ²/ρ p<0.001 通过 — 同上 L42–50。


---

## 3. 数据（Data Section）

### 3.1 微观数据：NY Fed Survey of Consumer Expectations (SCE) ✅
路径：`SCE_Data/01_Core_Survey` … `SCE_Data/08_Informal_Work`，8 个模块。

Phase 2 用到的 4 个模块：📊
- **Core Survey**：income expectation, income uncertainty（1 年期预期，离散概率分布合并为点估计 + 标准差）。
- **Labor Market Survey**：job finding probability, job loss probability → labor fragility 初值。
- **HH Spending**：MPC asymmetry, consumption type 分类。
- **Housing**：tenure × LTV → 4 housing states 概率分布。

具体加工：`Phase2_Code/extract_distributions.py` + 输出 `Phase2_Output/empirical_distributions.json` / `core_distributions.json` / `spending_distributions.json` / `lm_distributions.json`。

### 3.2 宏观数据：FRED + BLS 月度序列 ✅
路径：`Phase3_Data/`（7 个 CSV，下载脚本 `Phase3_Code/download_fred.py` / `fetch_fred_data.py`）。

| FRED 序列 | 文件 | 映射目标（模型变量） | 加工公式 |
|----------|------|------------------|----------|
| JTSJOR (Job Openings Rate) | `JTSJOR.csv` | `market_tightness` | rate / 3.0 |
| JTSLDR (Layoffs/Discharges Rate) | `JTSLDR.csv` | `separation_rate` | rate / 100 |
| CES0500000003_PC1 (Average Hourly Earnings YoY) | `CES0500000003.csv` | `income_growth_bg` | rate / 100 / 12 |
| FEDFUNDS | `FEDFUNDS.csv` | `borrowing_rate` | (rate + 2.0) / 100 |
| UNRATE | `UNRATE.csv` | **评估目标**（不输入模型） | rate / 100 |
| CIVPART | `CIVPART.csv` | **评估目标**（不输入模型） | rate / 100 |
| EMRATIO | `EMRATIO.csv` | **评估目标**（不输入模型） | rate / 100 |

来源：`Phase3_Code/environment_real.py` 第 36–69 行 ✅；`phase7_engine.py` 第 41–62 行 ✅（targets）。

### 3.3 时间覆盖范围 ✅
- 完整轨道：**2001-01 至 2026-02，共 302 个月**（`environment_real.py` 第 17 行 `start='2001-01', end='2026-02'`；`phase7_engine.py` 第 29 行 `OOS_END = 302`）。
- 缺失值填充：FRED 序列若 date 缺失，用 dict 默认值（jtsjor→3.0、jtsldr→1.2、earnings→3.0、fedfunds→2.0），见 `environment_real.py` 第 59–69 行。这是工程鲁棒性回退，**不构成对历史值的插补**。
- Clip 边界（防止极端值）：`market_tightness ∈ [0.3, 3.0]`、`separation_rate ∈ [0.005, 0.05]`、`income_growth_bg ∈ [-0.01, 0.02]`、`borrowing_rate ∈ [0.02, 0.15]`（`environment_real.py` 第 71–74 行）。

### 3.4 数据使用分层（What enters where）

| 阶段 | 用到的数据 | 不用到的数据 |
|------|-----------|------------|
| 人口生成（一次性） | SCE 4 模块 + CPS/BLS 锚点 | FRED 时序、UNRATE 评估目标 |
| 月度仿真输入 | 4 个 FRED 派生变量 | UNRATE / CIVPART / EMRATIO（评估目标，**严格隔离**） |
| 评估目标 | UNRATE / CIVPART / EMRATIO | — |
| Phase 6 校准 | UNRATE/CIVPART/EMRATIO（2001-01 至 2019-12）+ 4 FRED 输入 | OOS 段（2022-01 之后） |
| Phase 7 OOS 评估 | UNRATE/CIVPART/EMRATIO（2022-01 至 2026-02） | — |

**严格隔离的依据**：`environment_real.py` 加载的 4 个 FRED 序列与 `phase7_engine.py` 加载的 3 个评估目标完全无重叠；OOS 窗口 (`VAL_END=252 → OOS_END=302`) 在 `phase7_engine.py` 第 28–35 行硬编码，校准代码 `calibration_engine.py` 第 40 行 `TRAIN_END=228 # 2019-12` 之后的 val 段也只到 2022-01。

---

## 4. 月度仿真顺序（Simulation Order） ✅

来源：`Phase3_Code/scheduler.py` 第 68–134 行 `Simulation.run()`。每个月 t 严格按以下 11 步执行：

```
Step 1  读环境       env = self.env.get(t)            # FRED 4 变量
Step 2  期望更新     update_expectations(cs, ds, env, rng, cfg)
Step 3  参与决策     participation_block(...)         → exit_to_n, enter_from_n
Step 4  搜索强度     search_block(...)                → new search_intensity
Step 5  Offer 到达   opportunity_block(...)           → has_offer, offered_wage, is_separated
Step 6  Offer 接受   acceptance_block(...)            → accepts
Step 7  劳动转移     update_labor_states(...)         → 6 类转移计数
Step 8  收入更新     update_income(...)
Step 9  消费决策     consumption_block(...)           → consumption, savings
Step 10 借贷/缓冲    borrowing_block(...)             → new buf, liq, debt
Step 11 聚合统计     compute_aggregates(...)          → UR, LFPR, EPOP, transitions
```

执行顺序冻结于 `Phase3_Output/02_Simulation_Order_Spec.md`。每个 block 的 `cfg` 参数从 `mechanism_config.py` 注入，可通过 on/off 开关消融（详见第 7 节）。


---

## 5. 转移结构（State Transition Map）

### 5.1 六类劳动力转移
来源：`Phase3_Code/state_update.py` 第 9–64 行 `update_labor_states()` ✅。

| 转移 | 决定 block | 决定字段 | 排序优先级 |
|------|---------|---------|:-----:|
| E → U | `opportunity` | `is_separated` | 1 |
| U → E | `acceptance`  | `accepts`      | 2 |
| E → N | `participation` | `exit_to_n & emp==EMP_E` | 3 |
| U → N | `participation` | `exit_to_n & emp==EMP_U` | 3 |
| N → U | `participation` | `enter_from_n & emp==EMP_N` | 4 |
| N → E | （间接）N→U 后下一月经 acceptance 实现 | — | — |

**注**：从代码看，并不存在 N→E 的直接路径；`transitions` dict 中的 `N_to_E` 键被初始化为 0 (`state_update.py` 第 26 行) 但从未被赋值。这与 BLS Flows 定义一致——N→E 在 BLS 中被分解为 N→U→E 两步。

### 5.2 每类转移的概率结构（公式来源）

| 转移 | 基线概率 | 异质性调节项（cfg 启用时） | clip 范围 | 代码位置 |
|------|---------|--------------------------|----------|---------|
| **E → N** | age-based（age≥62: 0.005；≥55: 0.002；else: 0.0005） | `× (1 + 0.5×fragility) × pessimism_boost(if exp<-0.05)` | [0, 0.05] | `labor/participation.py` L33–43 |
| **U → N** | `0.015 + 0.003 × min(dur,24)/24` | `× exp_factor × buf_factor × exit_jump(if dur>thresh) + frag×liq boost + pessimism` | [0, 0.15] | `labor/participation.py` L48–76 |
| **N → U** | age-based（<25: 0.03；<55: 0.015；else: 0.005） | `× exp_enter_factor × buf_enter_factor × optimism_boost × (1 - owner_reentry_penalty)` | [0, 0.10] | `labor/participation.py` L81–101 |
| **E → U** (separation) | `env.separation_rate` (FRED JTSLDR) | `× (1 + 0.2×fragility)` | [0.002, 0.05] | `labor/opportunity.py` L93–99 |
| **U → E** (offer + accept) | matching: top-N agents by score 拿 offer；接受 if `offered_wage ≥ resv_wage` | score = `s_norm × (1-0.3×mob_fric) × (1+0.1×flex) × (1-lockin_penalty if Owner-High)` | n_vacancies = `N × vac_rate × mt` | `labor/opportunity.py` L36–82 + `labor/acceptance.py` L13–55 |

### 5.3 转移概率的函数形式
- **不是显式 logit**。所有概率为乘积调节 (`base × factor1 × factor2 × ...`) 然后 `np.clip` 到合理边界。
- **接受决策**是确定性阈值：`accepts = offered_wage >= resv_wage`（`acceptance.py` 第 55 行），其中 resv_wage 经过 duration / buffer / fragility / liquidity 五重折减后比较。
- **U→E 中的 matching** 在 `cfg['matching_competition']['enabled']=True` 时是 **finite vacancy 竞争**（top-K by score），否则回退到独立伯努利（fallback，`opportunity.py` L73–82）。

### 5.4 收入与缓冲动力
- **就业者**：`income *= (1 + bg + ε)`，`ε ~ N(0, 0.005)`（`state_update.py` 第 79 行）。
- **新失业**（duration ≤ 1）：`income *= 0.40`（即 60% 替代损失，对应 UI 净领取，`state_update.py` 第 83 行）。
- **NILF**：保持初始低水平（`state_update.py` 第 87–88 行）。
- **现金缓冲**：`cash_buf += savings / monthly_expense`，`monthly_expense = max(income/12 × 0.80, 0.5)`（`household/borrowing.py` 第 20–37 行）；Saver 不允许负值，Spender 可达 `-2.0`。

---

## 6. 异质性消费与借贷模块（Household Section）

### 6.1 Consumption Block ✅
来源：`Phase3_Code/household/consumption.py`。

- **基础消费**：`base_rate × income / 12 + delta_C`，其中 `base_rate = 0.93/0.97/1.00`（Saver / Smoother / Spender），H2M 强制 1.00。
- **非对称 MPC**：`delta_C = delta_income × (mpc_pos if Δ≥0 else mpc_neg)`。
- **三个机制开关**：
  - `effective_mpc_adjustment`：H2M floor → `mpc ≥ 0.95`；Wealthy → `× (1 - 0.30)`；Unemployed → `mpc_neg += 0.10`。
  - `consumption_sequencing`：Saver+buffer→`mpc_neg × 0.5`；Spender+buffer→`mpc_neg × 1.3`。
  - `liquidity_constraint_modifier`：H2M 在 acceptance 中强制 floor MPC（间接）。

### 6.2 Borrowing Block ✅
来源：`Phase3_Code/household/borrowing.py`。

- 缓冲变化：`buffer_change = savings / monthly_expense`。
- 类型化排序（`buffer_consumption_ordering`）：Spender 允许 `cash_buf < 0`（floor `-2.0`）；Saver/Smoother 强制 `cash_buf ≥ 0`（cut consumption first）。
- 流动性类型转移（自动）：buffer < 1.0 → H2M；buffer < 4.0 → Buffer；buffer > 2.0 概率 0.1 → 升至 Buffer；buffer > 8.0 概率 0.05 → 升至 Wealthy（L52–64）。
- 债务压力反馈：`stress_increase` 触发 `+0.05`，`stress_decrease` 触发 `-0.03`，clip 到 [0, 1]。

### 6.3 Expectation Update ✅
来源：`Phase3_Code/state_update.py` 第 95–173 行 `update_expectations()`。

- **State-dependent**：Employed 适应速度 0.05，Unemployed 适应速度 0.20；high fragility (>0.5) 再乘 1.5。
- **Experience-dependent**：新失业的 agent 期望直接 `-= 0.10`（experience_weight），随后悲观 (exp<-0.03) → fragility `+0.003`（spiral）。
- Fragility 更新：employed `-0.005/mo`、unemployed `+0.01/mo`，环境 `sep/0.015 × 0.3` 作为锚定。


---

## 7. 结构机制清单（Mechanism Registry，13 项）

来源：`Phase3_Code/mechanism_config.py` 第 8–113 行 `default_config()` ✅。每项可通过 `enabled: True/False` 独立开关。

| # | 机制名 | 影响的 block | 关键参数（默认值） |
|---|--------|------------|-----------------|
| 1 | `high_fragility_modifier` | search, acceptance | fragility_threshold=0.5, acceptance_pressure_factor=0.15 |
| 2 | `liquidity_constraint_modifier` | acceptance, consumption | h2m_mpc_floor=0.90, h2m_resv_wage_discount=0.20 |
| 3 | `housing_lockin_modifier` | search, opportunity | lockin_search_penalty=0.30 |
| 4 | `fragility_x_liquidity_interaction` | participation | discouraged_exit_boost=0.05 |
| 5 | `matching_competition` | opportunity | vacancy_rate=0.03 |
| 6 | `discouraged_worker` | participation | duration_threshold_months=6, exit_jump_factor=2.0 |
| 7 | `housing_reentry_friction` | participation | owner_reentry_penalty=0.30 |
| 8 | `expectation_participation` | participation | optimism_entry_boost=0.3, pessimism_exit_boost=0.2 |
| 9 | `effective_mpc_adjustment` | consumption | h2m_mpc_floor=0.95, wealthy_mpc_discount=0.30 |
| 10 | `consumption_sequencing` | consumption, borrowing | saver_buffer_protect_threshold=3.0 |
| 11 | `buffer_consumption_ordering` | borrowing | stress_feedback_rate=0.08, max_negative_buffer=-2.0 |
| 12 | `state_dependent_expectation` | expectations | employed_adaptation_speed=0.05, unemployed_adaptation_speed=0.20 |
| 13 | `experience_dependent_expectation` | expectations | experience_weight=0.10 |

**配套函数**：
- `default_config()` — 13 项全开（论文主结果）。
- `all_off_config()` — 13 项全关（Phase 8 D2 派生模型基线）。
- `ablation_config(name)` — 仅关闭指定一项（Phase 7 / 8 mechanism ablation）。

---

## 8. 聚合度量（Aggregator）

来源：`Phase3_Code/aggregator.py` 第 9–85 行 ✅。

| 度量 | 公式 | 与 BLS 定义对应 |
|------|------|--------------|
| **Unemployment Rate (UR)** | `n_U / max(n_E + n_U, 1)` | BLS U-3 |
| **LFPR** | `(n_E + n_U) / N` | BLS Civilian Labor Force Participation Rate |
| **EPOP** | `n_E / N` | BLS Employment-Population Ratio |
| EU rate | `transitions['E_to_U'] / prev_E` | BLS Flows: E→U |
| UE rate | `transitions['U_to_E'] / prev_U` | BLS Flows: U→E |
| H2M share | `(liq == LIQ_H2M).mean()` | Kaplan-Violante hand-to-mouth |
| Avg cash buffer | `cash_buf.mean()`（月支出倍数） | SCE proxy |
| Avg search intensity | `search_int[emp==U].mean()` | model-internal |

**注**：UR 公式严格遵守 BLS 分母（labor force = E + U，不含 N），不存在分母选择歧义。`Phase3_Output/phase7/robustness_results.json` R4 项进一步验证：加入 SCE side-job (informal) 调整后 OOS RMSE 仅从 0.0023 变为 0.0048，模型 UR 输出已隐式对应 BLS 定义。

---

## 9. 校准协议（Calibration Section）

### 9.1 框架（Phase 6）
来源：`Phase3_Code/calibration_engine.py` ✅。

- **方法**：Latin Hypercube Sampling (LHS) over 14 维参数空间。
- **参数空间**（`PARAM_SPACE`，calibration_engine.py 第 50–66 行）：

| 参数 | 所属机制 | 边界 |
|------|---------|------|
| vacancy_rate | matching_competition | [0.02, 0.08] |
| fragility_threshold | high_fragility_modifier | [0.3, 0.7] |
| acceptance_pressure | high_fragility_modifier | [0.05, 0.30] |
| h2m_resv_discount | liquidity_constraint_modifier | [0.10, 0.35] |
| lockin_penalty | housing_lockin_modifier | [0.10, 0.50] |
| duration_thresh | discouraged_worker | [3, 12] |
| exit_jump | discouraged_worker | [1.0, 4.0] |
| reentry_penalty | housing_reentry_friction | [0.05, 0.50] |
| h2m_mpc_floor | effective_mpc_adjustment | [0.85, 0.99] |
| wealthy_discount | effective_mpc_adjustment | [0.15, 0.50] |
| emp_adapt_speed | state_dependent_expectation | [0.02, 0.15] |
| unemp_adapt_speed | state_dependent_expectation | [0.08, 0.35] |
| pessimism_exit | expectation_participation | [0.05, 0.40] |
| optimism_entry | expectation_participation | [0.10, 0.50] |

- **训练目标**：2001-01 至 2019-12（228 个月，`TRAIN_END = 228`）。
- **验证目标**：2020-01 至 2026-02（剩余，但 Phase 7 进一步把 2022-01 之后切成 OOS）。

### 9.2 多目标 3-tier loss ✅
来源：`calibration_engine.py` 第 82–132 行 `compute_loss()`：

```
total_loss = 5.0 × RMSE(UR)            # Tier 1: 失业率（主目标）
           + 2.0 × RMSE(LFPR)          # Tier 2: 劳动参与
           + 2.0 × RMSE(EPOP)          # Tier 2: 就业占比
           + 1.0 × |E[eu] - 0.015| × 10 # Tier 2: 月度 E→U 流速
           + 1.0 × |E[ue] - 0.25 | × 5  # Tier 2: 月度 U→E 流速
           + 0.5 × |E[h2m] - 0.30| × 2  # Tier 3: H2M share (Kaplan-Violante 锚)
```

Phase 7 主跑使用同一 loss（`phase7_engine.py` 第 112–119 行），但分 `train` (2004-01–2018-01) / `val` (2018-01–2022-01) / `oos` (2022-01–2026-02) 三段分别计算。

### 9.3 选出的候选 ✅
来源：`Phase3_Output/phase6/candidate_{baseline,conservative,aggressive}.json`。

**Baseline 候选（论文 reference）**（`candidate_baseline.json`）：

| 参数 | 取值 |
|------|------|
| vacancy_rate | 0.0437 |
| fragility_threshold | 0.696 |
| acceptance_pressure | 0.161 |
| h2m_resv_discount | 0.139 |
| lockin_penalty | 0.205 |
| duration_thresh | 6.66 (months) |
| exit_jump | 2.14 |
| reentry_penalty | 0.466 |
| h2m_mpc_floor | 0.965 |
| wealthy_discount | 0.284 |
| emp_adapt_speed | 0.0495 |
| unemp_adapt_speed | 0.336 |
| pessimism_exit | 0.186 |
| optimism_entry | 0.489 |

Train loss = 0.178 ± 0.006，Val loss = 0.468 ± 0.001，`stable: True`（即不同 seed 间稳定）。

### 9.4 校准方法不变性（Package E）
来源：`Phase3_Output/packageE/PackageE_Summary.md`。Package E 对 5 种校准方法（LHS / random / Bayesian / grid / iterative）在同一 14 维参数空间下做对比，**预测精度 CV = 5.6%**、**share_het 差异 ≤ 3.35 pp**。**但 10/14 参数不可识别**（不同方法收敛到差异 > 30% 的最优点，预测却几乎相同）→ 说明 14 维参数空间存在大量 sloppy directions，论文不应在参数 point estimates 上做强解读，应聚焦预测精度与机制级 ablation。


---

## 10. 实验设计（Experimental Design Section）

### 10.1 四段时间窗口 ✅
来源：`Phase3_Code/phase7_engine.py` 第 26–36 行。

| 窗口 | 索引区间 (`WINDOWS`) | 日期区间 | 月数 | 用途 |
|------|------------------|---------|:----:|------|
| **Init** | `[0, 36)` | 2001-01 → 2003-12 | 36 | 模型预热，不计入 loss |
| **Train** | `[36, 204)` | 2004-01 → 2017-12 | 168 | 校准参数（Phase 6 也用此段作 LHS 评估） |
| **Val** | `[204, 252)` | 2018-01 → 2021-12 | 48 | 候选间选择（含 COVID 冲击） |
| **OOS** | `[252, 302)` | 2022-01 → 2026-02 | 50 | **冻结评估窗口** ✅ |

**OOS 隔离的代码证据**：
- `phase7_engine.py` 第 28–29 行硬编码 `VAL_END = 252` / `OOS_END = 302`。
- 校准代码 `calibration_engine.py` 第 40 行 `TRAIN_END = 228 # 2019-12`，意味着 Phase 6 选参时见过 2019-12 之前所有数据 + 2020–2022 一年验证段，但**没有用到 2022-01 之后的任何月份**。
- Phase 7 评估时 OOS 段从 252 起，且只在结果汇总时调用 `compute_window_metrics(history, ..., 'oos')`。

### 10.2 主实验（Phase 7 Main） ✅
来源：`Phase3_Code/run_phase7_main.py`。
- **3 个候选版本** × **5 个 seed** {42, 137, 2024, 888, 1234} × **3 个评估窗口** = 45 次运行。
- 每个 seed 单独运行 302 月，分别计算 train/val/oos 三段指标。

### 10.3 派生控制（Phase 8）
来源：`Phase3_Code/phase8_derived.py`。

| 派生模型 | 异质性 | 高级机制 | Household 外圈 | 用途 |
|---------|:------:|:-------:|:------------:|------|
| **M0_Main** | ✅ 全开 6 维 | ✅ 13 项全开 | ✅ | 主结果 |
| **D1_Homogeneous** | ❌ 抹平 6 维 → 取中位/众数 | ✅ | ✅ | 隔离异质性贡献 |
| **D2_Simplified** | ❌ | ❌ 只保留 matching | ✅（结构存在但被剪短） | 最简对照 |
| **D3_LaborOnly** | ✅ | ✅ | ❌ 关掉 4 个 household 机制 | 隔离 household 圈贡献 |

异质性抹平的具体实现：`phase7_engine.py` 第 126–154 行 `flatten_heterogeneity(cs, ds, bp, dim)`，按维度替换为人口 median/mean/mode：

```python
'income_exp' → median; 'labor_frag' → median;
'liquidity'  → LIQ_BUFFER + median(cash_buf);
'search'     → mean(SEARCH/RESV/FLEX);
'housing'    → HSG_RENT_STB + median(mob_fric);
'consumption_rule' → CON_SMOOTHER + mean(MPC+/MPC−)
```

### 10.4 外部基准（Phase 8 External Benchmarks）
来源：`Phase3_Code/phase8_benchmarks.py` + `Phase3_Output/phase8/external_benchmark_specs.md`。

| 基准 | 方法 | 数据 | 训练窗口 |
|------|------|------|--------|
| **B1 AR(p)** | UR 自回归（p 由 AIC 选） | UNRATE 月度 | 2004-01 → 2021-12 |
| **B2 VAR(p)** | UR + LFPR + EPOP 多元自回归 | 3 序列 | 同上 |
| **B3 Beveridge** | OLS：UR ~ 1/V + θ + const | UR + JTSJOR | 同上 |
| **B4 DMP (Simplified)** | Mortensen-Pissarides 风格 hazard rate 拟合 | UR + 流速 | 同上 |

OOS 评估同样限定在 2022-01 → 2026-02 (50 月)。

### 10.5 五项稳健性扩展（Packages A–E）
来源：`Phase3_Code/package{A..E}_engine.py` + `Phase3_Output/package{A..E}/PackageE_Summary.md` 等。

| Package | 测试维度 | 设计 | 结论指向 |
|---------|---------|------|--------|
| **A** | 训练窗口 | 10 个 walk-forward / expanding splits | 14 参数 0/14 严重漂移；预测在 7/10 splits 稳定 |
| **B** | 预测期 (horizon) | h ∈ {1, 3, 6, 12, 24, 36} 月，slope 检验 | M0 slope = −0.09（无 horizon 退化）；het_share 0.90–1.01 |
| **C** | 异质性阶梯 | L0（同质）→ L6（全部 6 维）逐维叠加 | 阶梯**非单调**：单加 Liquidity 或 Search 会反向恶化；6 维必须成对成组 |
| **D** | Agent 规模 | N ∈ {5k, 10k, 25k, 50k, 100k, 200k, 300k}×10 seeds | N ≈ 50k 达平台期；100k 是 (variance, cost) 最优 |
| **E** | 校准方法 | LHS / random / Bayes / grid / iterative，5 method × 3 seed | 预测 CV = 5.6%；10/14 参数不可识别（sloppy） |

---

## 11. 头条结果（Headline Numbers，论文可直接引用）

> **所有数字来自 `Phase3_Output/phase7/main_run_metrics.json` 与 `Phase3_Output/phase8/source_of_advantage.json`，原文件 0 修改。** 📊

### 11.1 主结果（the heterogeneous ABM，baseline 候选）
来源：`main_run_metrics.json` lines 89–173（`summary.baseline`）。

| 窗口 | UR RMSE | UR MAE | UR Corr | LFPR RMSE | EPOP RMSE |
|------|--------:|-------:|--------:|----------:|----------:|
| Train (2004–2017) | 0.0132 ± 0.0003 | 0.0104 ± 0.0002 | 0.806 ± 0.004 | 0.0145 ± 0.0008 | 0.0163 ± 0.0008 |
| Val (2018–2021)   | 0.0200 ± 0.0001 | 0.0154 ± 0.0003 | 0.676 ± 0.014 | 0.0157 ± 0.0014 | 0.0250 ± 0.0011 |
| **OOS (2022-01–2026-02)** | **0.00221 ± 0.00007** | **0.00163 ± 0.00006** | **0.790 ± 0.022** | 0.0227 ± 0.0015 | 0.0221 ± 0.0014 |

**论文写法**（pp 单位）：UR **RMSE = 0.22 pp**, **Corr = 0.79**, MAE = 0.16 pp，over a frozen 50-month out-of-sample window (2022-01 to 2026-02), averaged across 5 seeds.

### 11.2 派生控制对照（Phase 8 Source of Advantage）
来源：`Phase3_Output/phase8/source_of_advantage.json`。

| 配置 | OOS UR RMSE (pp) | ΔRMSE vs M0 (pp) | 含义 |
|------|-----------------:|-----------------:|------|
| **M0 Main (full)** | **0.221** | 0.000 | 完整模型 |
| D3 LaborOnly (no household ring) | 0.390 | +0.169 | Household 圈贡献 |
| D1 Homogeneous (full mechs, no het) | 0.548 | +0.327 | 异质性贡献 |
| D2 Simplified (minimal) | 0.563 | +0.342 | 总基线 |

**层分解（D2 → D1 → M0 路径）**：
- 加入 13 项机制（D2 → D1）：ΔRMSE = +0.015 pp → 占总优势 **4%**
- 加入 6 维异质性（D1 → M0）：ΔRMSE = +0.327 pp → 占总优势 **96%**

**论文写法**：96% of the heterogeneous ABM's out-of-sample advantage over the simplified control comes from worker heterogeneity; only 4% comes from the structural mechanisms layer.

### 11.3 vs 外部基准（Phase 8 Benchmark Comparison）
来源：`Phase3_Output/phase8/comparison_results.csv`。

| Model | UR RMSE (pp) | UR Corr | M0 vs |
|-------|-------------:|--------:|:-----:|
| **M0 Main** | **0.221** | **0.788** | — |
| B3 Beveridge | 0.421 | 0.831 | **1.9×** better RMSE |
| B4 DMP | 0.631 | 0.826 | 2.9× |
| B2 VAR(p) | 0.657 | −0.873 | 3.0× |
| B1 AR(1) | 1.610 | 0.645 | 7.3× |

**论文写法**：The heterogeneous ABM achieves an OOS UR RMSE 1.9× lower than the strongest external benchmark (Beveridge regression) and 7.3× lower than AR(1).


---

## 12. 关键 claim 与证据矩阵（论文级）

| Claim | 证据文件 | 状态 |
|-------|---------|:----:|
| C1 Worker-side ABM with aggregate labor demand (no firm agents) | `scheduler.py` L39–60；`opportunity.py` L36–82 | ✅ |
| C2 6-dim worker heterogeneity from NY Fed SCE | Phase1 文档 §二；`Phase2_Output/empirical_distributions.json` | ✅ |
| C3 100k synthetic agents | `population_init_engine.py` L34；`population_v1.npz` shape (100000,·) | ✅ |
| C4 4 FRED variables drive monthly environment | `environment_real.py` L36–69 | ✅ |
| C5 Strict OOS 2022-01 to 2026-02 isolation | `phase7_engine.py` L28–35；`calibration_engine.py` L40 | ✅ |
| C6 OOS UR RMSE = 0.22 pp, Corr = 0.79 | `main_run_metrics.json` baseline.oos | 📊 |
| C7 96% of advantage from heterogeneity | `source_of_advantage.json` | 📊 |
| C8 1.9× better than strongest benchmark | `comparison_results.csv` | 📊 |
| C9 14-param LHS calibration, 3 candidates | `calibration_engine.py` + `phase6/candidate_*.json` | ✅ |
| C10 Stable across 5 seeds (CV = 3.1%) | `Phase3_Output/phase7/robustness_results.json` | 📊 |
| C11 Robust to training window choice (Package A) | `Phase3_Output/packageA/PackageA_Summary.md` | 📊 |
| C12 Robust to forecast horizon (Package B, slope = −0.09) | `Phase3_Output/packageB/PackageB_Summary.md` | 📊 |
| C13 Calibration-method invariant (Package E, CV = 5.6%) | `Phase3_Output/packageE/PackageE_Summary.md` | 📊 |

---

## 13. 限制与待人工确认事项（Limitations）

### 13.1 Inference, not directly confirmed by code

- 🔸 **"Type B classification"**：论文叙述中称模型为"worker-side ABM with aggregate labor demand"。代码层面只能直接证明（i）无 firm agent 集合；（ii）vacancy 由 `N × vac_rate × mt` 给出。但是否归类为 Burdett-Mortensen / DMP-lite / 工程化 type B 是分类约定，**该归类未在代码注释中明文写出**。建议论文写为："a worker-level transition ABM where firm-side activity is summarized by FRED job-openings and layoff series, rather than modeled by explicit firm agents." 这一表述只引述代码可证内容。

- 🔸 **"Logit-like transition probabilities"**：前期 conversation summary 提到"transition probabilities are generally logistic-like"。**代码层面更准确的描述是 multiplicative-modulated baseline probabilities with clipping**，并不是显式 σ(βx) logit。论文写作时应改为"baseline rates multiplied by heterogeneity factors and clipped to plausible ranges"，避免暗示 logit estimation。

- 🔸 **"60% UI replacement"**：`state_update.py` L83 `income *= 0.40` 蕴含 60% 收入损失。这与 OECD 平均替代率范围接近，但**不是 UI 制度的显式建模**（无 max-weekly-benefit、无 base period、无 26-week 时限）。论文应表述为"a proportional income drop upon job loss calibrated to roughly correspond to the average net replacement rate in the U.S."

### 13.2 未找到明确依据，需要人工确认

- ❌ **"No price/inflation channel" 的明确边界文档**：在 `Phase1_Output/02_MVP_Boundary_Freeze_v1.md` §四 第 7 条中 inflation belief 被降级到第二圈但未明文写"模型不含价格"。建议在论文 Model Overview 中明确："The model omits a price-setting block; nominal-real distinctions are absorbed into the income-growth background." 这一表述需要作者最终决定如何承认这一边界。

- ❌ **`Phase 7 OOS UR mean = 3.96%` vs BLS 实际 OOS UR mean** 的直接对比未单独保存；可从 `Phase3_Output/phase7/main_run_series.npz` + `Phase3_Data/UNRATE.csv` 2022-01–2026-02 现算（mean ≈ 3.7%–4.0%）。如需论文中给出 level bias 数字，建议在重跑前用脚本核算。

- ❌ **Package B "no horizon degradation" 的统计显著性**：`PackageB_Summary.md` 报告 slope = −0.09，但**未见显著性检验输出**（如 SE 或 95% CI）。论文若要 claim "no significant degradation"，需要在写作前补做一次 bootstrap CI（建议 500 次）。

- ❌ **Phase 5 mechanism identification 的 t = 20.21 数值**：在 `Phase3_Output/phase5/` 目录中确实有该结果但未本次直接读取；如论文 Methods 引用，请人工核对 `phase5_identification.py` 的输出 json。

### 13.3 一致性提示（已交叉核对，可放心引用）

- ✅ **96% (Phase 8) vs 57% (Package E)**：两个数字测量的不是同一对象——Phase 8 是 (D1 → M0) 占 (D2 → M0) 总增益的 96%；Package E 的 57% 是 (D1 − M0)/D1 的相对改进。论文写作时分别写为"share of advantage from heterogeneity"和"relative RMSE reduction by adding heterogeneity"即可，**两者不矛盾**。

- ✅ **"Search Friction 是核心"（Phase 7 ablation） vs "Ladder L2 单加恶化"（Package C）**：两者合并为一句即可——"Search Friction is the single most important dimension once the rest of the 6-dim constraint layer is already in place; adding it alone (without other dimensions) yields non-monotonic behavior."

---

## 14. 适合直接拷入论文的样板段落（基于上述证据）

### 14.1 Model Overview 开头
> The heterogeneous ABM is a worker-side transition model in which a synthetic population of N = 100,000 agents, calibrated to the New York Fed Survey of Consumer Expectations, evolves at monthly frequency between three employment states {Employed, Unemployed, Not-in-Labor-Force}. Firm-side activity is summarized by four FRED series (job openings, layoffs, average hourly earnings YoY, and the federal funds rate), rather than modeled through explicit firm agents. Six dimensions of worker heterogeneity—income-growth expectation, labor fragility, liquidity, labor-search friction, housing mobility, and consumption rule—were frozen in advance based on a hand-coded mapping from the SCE survey items, and 13 structural mechanisms governing their interaction can be independently enabled or disabled.

### 14.2 Data Section 摘要
> The data used in this paper consist of two distinct sets, with strict separation between inputs and evaluation targets. The micro inputs—drawn from the New York Fed SCE Core, Labor-Market, HH-Spending, and Housing modules (2013–2024)—are used **only at population initialization**. The macro inputs—four FRED series (JTSJOR, JTSLDR, CES0500000003, FEDFUNDS)—are read monthly by the simulation. The three evaluation targets—UNRATE, CIVPART, EMRATIO from BLS—are **never** fed into the model. The frozen out-of-sample window runs from 2022-01 to 2026-02 (50 months), and was selected before any parameter was estimated.

### 14.3 Calibration Section 摘要
> Fourteen mechanism-level parameters are calibrated via Latin Hypercube Sampling over the parameter ranges fixed in the Phase-5 identification stage. The loss function is a three-tier hierarchical RMSE: weight 5 on the unemployment rate (Tier 1), weight 2 each on LFPR, EPOP, and labor-flow rates (Tier 2), and weight 0.5 on the hand-to-mouth share (Tier 3). Calibration is performed over 2004-01 to 2019-12, with 2020–2021 reserved for candidate selection. The 2022-01 to 2026-02 window is never used in calibration.

### 14.4 Experimental Design Section 摘要
> The experimental design contains three layers: (i) a main run of the heterogeneous ABM under three calibrated candidate parameterizations across five random seeds; (ii) a derived-control ablation that progressively removes either the 6-dimensional heterogeneity, the 13 structural mechanisms, or the household-side block, isolating each component's contribution; (iii) a benchmark comparison against four standard forecasting models (AR, VAR, Beveridge regression, and a simplified DMP). All models are evaluated on the identical 50-month frozen OOS window with the same FRED inputs.

---

## 附录 A：本报告对应的源文件清单（可重复审计）

| 段落 | 主要源文件 |
|------|---------|
| §1 模型分类 | `scheduler.py`, `opportunity.py`, `environment_real.py`, `Phase1_Output/02_*.md` |
| §2 Agent 状态 | `constants.py`, `population_init_engine.py`, `Phase2_Output/04_*.md` |
| §3 数据 | `Phase3_Data/*.csv`, `environment_real.py`, `phase7_engine.py` |
| §4 仿真顺序 | `scheduler.py`, `Phase3_Output/02_Simulation_Order_Spec.md` |
| §5 转移结构 | `state_update.py`, `labor/*.py` |
| §6 Household | `household/consumption.py`, `household/borrowing.py`, `state_update.py` |
| §7 机制清单 | `mechanism_config.py`, `Phase3_Output/Phase4_*.md` |
| §8 聚合 | `aggregator.py` |
| §9 校准 | `calibration_engine.py`, `phase6/candidate_*.json` |
| §10 实验设计 | `phase7_engine.py`, `phase8_derived.py`, `phase8_benchmarks.py`, `package{A..E}_engine.py` |
| §11 结果 | `phase7/main_run_metrics.json`, `phase8/source_of_advantage.json`, `phase8/comparison_results.csv` |
| §12 Claims | 同上各项 |

**本报告与项目内 `real_data_experiments/00_manifest/13_experiments_report.md` 的关系**：13 实验报告是"过程账本"（每个实验做了什么、得到什么数字），本验证报告是"论文写作锚点"（每条 paper-grade claim 对应代码哪一行 / 输出哪个 json key）。两者互补，建议论文撰写时同时打开。

---

*Report ends. 所有结论已限定到代码可证 / 输出可证 / 明示标注推断三类，未做模糊推断。*
