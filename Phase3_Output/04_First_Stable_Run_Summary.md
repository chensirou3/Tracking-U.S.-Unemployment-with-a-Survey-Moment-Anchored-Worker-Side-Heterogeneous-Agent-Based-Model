# First Stable Run Summary

> Phase 3 — Main Model Core Engine

## 运行配置

| 参数 | 值 |
|------|-----|
| N (agents) | 100,000 |
| T (months) | 120 |
| Scenarios | baseline, recession |
| Seed | 42 |
| 运行时间 | ~110s per scenario |

## Baseline Scenario 结果

| 指标 | Mean | Min | Max | 说明 |
|------|------|-----|-----|------|
| Unemployment Rate | 9.1% | 5.3% | 11.1% | 从初始6.4%上升到稳态~9% |
| LFPR | 67.1% | 62.8% | 69.8% | 从63%逐步上升 |
| EPOP | 61.0% | 57.5% | 63.2% | 稳定 |
| E→U rate | 1.24%/mo | 1.1% | 1.4% | 合理 |
| U→E rate | 14.2%/mo | 12.5% | 18.5% | 略低于BLS ~25% |
| H2M share | 30.9% | 25.5% | 38.3% | 从26%上升 |
| Avg cash buffer | 3.64 mo | 2.72 | 5.63 | 下降趋势 |

## Recession Scenario 结果

| 指标 | 稳态(t<36) | 衰退峰值(t≈60) | 恢复后(t=120) |
|------|-----------|---------------|-------------|
| Unemployment Rate | ~9% | ~17% | ~9% |
| LFPR | ~67% | ~66% | ~69% |
| E→U rate | ~1.2% | ~1.6% | ~1.2% |
| U→E rate | ~14% | ~9% | ~14% |
| H2M share | ~30% | ~40% | ~32% |
| Avg cash buffer | ~3.6 mo | ~2.0 mo | ~3.2 mo |

## 定性验证

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 模型闭环不崩溃 | ✅ | 120个月稳定运行 |
| UR 有合理稳态 | ✅ | ~9%（偏高但结构合理） |
| 衰退期 UR 上升 | ✅ | 峰值 +8pp |
| 衰退后恢复 | ✅ | 恢复到基线水平 |
| LFPR 合理 | ✅ | 62-70% |
| E→U 和 U→E 方向正确 | ✅ | 衰退：E→U↑ U→E↓ |
| H2M 比例在衰退中上升 | ✅ | 30→40% |
| Cash buffer 在衰退中下降 | ✅ | 3.6→2.0 |
| 异质性影响决策 | ✅ | fragility, buffer, mobility 都进入决策 |

## 已知偏差（阶段 4 调整）

| 偏差 | 当前值 | 目标值 | 原因 | 修复方向 |
|------|--------|--------|------|---------|
| 稳态 UR 偏高 | ~9% | 4-5% | U→E率不足 | 提高alpha或降低resv_wage |
| U→E 率偏低 | 14%/mo | 25%/mo | offer×acceptance乘积不够 | calibration |
| LFPR 初始偏低 | 63% | 63% | 初始人口N比例偏高 | 调整初始E/U/N比例 |

## 文件清单

| 文件 | 说明 |
|------|------|
| `Phase3_Output/run_baseline.npz` | Baseline 120月时间序列 |
| `Phase3_Output/run_recession.npz` | Recession 120月时间序列 |
| `Phase3_Output/output_schema.json` | 输出变量定义 |
| `Phase3_Output/figures/first_stable_run.png` | 6面板序列图 |
| `Phase3_Output/figures/household_indicators.png` | 家庭指标图 |
