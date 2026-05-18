# 文档 2：MVP 边界冻结表（MVP Boundary Freeze v1）

> 版本：v1.0
> 阶段：Phase 1 — Heterogeneity Audit & Engineering
> 冻结日期：2026-04-14

---

## 一、三圈架构总览

```
┌─────────────────────────────────────────────────────────┐
│                   第一圈：MVP 主系统（6维）               │
│  Income Growth Exp · Labor Fragility · Liquidity Frag   │
│  Labor Search Fric · Housing Mobility · Consumption Adj │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                第二圈：扩展系统（4维）                     │
│  Inflation Belief · Credit Access · Numeracy · Risk Pref│
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│             第三圈：校准/验证层（2+1维）                   │
│  Balance Sheet Comp · Policy Sensitivity                │
│  Informal Work（分布参考，非个体级数据源）                  │
└─────────────────────────────────────────────────────────┘
```

---

## 二、冻结边界表

| # | 异质性名称 | 层级 | In MVP? | 原层级 | 变动 | 冻结理由 |
|---|-----------|------|---------|-------|------|---------|
| 1 | Income Growth Expectation | 第一圈 MVP | ✅ | MVP | 无变动 | 收入预期直接影响求职强度、保留工资、劳动参与决策 |
| 2 | Labor Fragility | 第一圈 MVP | ✅ | MVP | 无变动 | 失业概率+再就业概率是失业率的微观基础 |
| 3 | Liquidity Fragility | 第一圈 MVP | ✅ | MVP | 无变动 | 流动性约束决定搜索持续能力和被迫接受次优工作 |
| 4 | Labor Search Friction | 第一圈 MVP | ✅ | 第二阶段 | ⬆️ 提升 | 保留工资和搜索强度直接决定失业持续期和就业转移概率 |
| 5 | Housing Mobility Friction | 第一圈 MVP | ✅ | MVP | 无变动 | 住房锁定→地理流动性下降→就业匹配效率降低 |
| 6 | Consumption Adjustment Rule | 第一圈 MVP | ✅ | MVP | 无变动 | MPC异质性影响总需求反馈到劳动需求；消费缓冲策略影响搜索行为 |
| 7 | Inflation Belief Heterogeneity | 第二圈 扩展 | ❌ | MVP | ⬇️ 降级 | 传导链过长（通胀预期→工资→产出→就业），第一版无价格设定模块 |
| 8 | Credit Access Constraint | 第二圈 扩展 | ❌ | 第二阶段 | 无变动 | 与Liquidity Fragility功能重叠；第二阶段borrowing block扩展时引入 |
| 9 | Numeracy & Planning | 第二圈 扩展 | ❌ | 第二阶段 | 无变动 | 慢变量，MVP阶段可用教育水平代理 |
| 10 | Risk Preference | 第二圈 扩展 | ❌ | 第二阶段 | 无变动 | 影响工作类型选择但非失业率主通道 |
| 11 | Balance Sheet Composition | 第三圈 校准 | ❌ | 校准 | 无变动 | HH Finance已停更，仅用于横截面分布校准 |
| 12 | Policy Sensitivity | 第三圈 校准 | ❌ | 校准 | 无变动 | 用于政策冲击情景分析，非核心预测变量 |
| — | Informal Work | 第三圈 分布参考 | ❌ | 分布参考 | 无变动 | 来自不同调查（波士顿联储），只用于分布合理性验证 |

---

## 三、MVP 6 维与主预测目标的传导机制

| MVP 维度 | 对失业率的一阶传导 | 对辅助劳动指标的传导 |
|---------|-------------------|-------------------|
| Income Growth Expectation | 预期收入↓ → 搜索更焦虑 → 降低保留工资 → 加速匹配但质量下降 | 影响劳动参与率、就业-非劳动力转移 |
| Labor Fragility | 高脆弱性 → 高失业概率 → 直接推高失业率 | 影响失业持续期分布、U-E/E-U转移率 |
| Liquidity Fragility | 缓冲不足 → 无法长期搜索 → 被迫接受次优offer或退出 | 影响就业质量、非自愿兼职率 |
| Labor Search Friction | 高保留工资 → 拒绝offer → 延长失业期；低搜索强度 → 低offer率 | 影响失业持续期、空缺填充率 |
| Housing Mobility Friction | 住房锁定 → 无法迁移 → 本地搜索池受限 → 匹配效率下降 | 影响地理错配、区域失业率差异 |
| Consumption Adjustment Rule | 高MPC → 失业冲击→消费骤降→总需求↓→进一步裁员 | 影响总需求-就业反馈环路强度 |

---

## 四、冻结规则

1. **MVP 6 维在阶段 1-3 期间不得移除或替换**，只允许在构造方法上优化。
2. **第二圈 4 维只能在阶段 4 之后引入**，且必须写清引入理由和影响范围。
3. **第三圈维度永远不进入主模型动态循环**，只用于初始化校准和结果验证。
4. **Informal Work 永远不作为个体级数据源**，只作为分布参考。
5. **任何层级变动必须在变动时更新本文档版本号**。

---

## 五、冻结状态

| 项目 | 状态 |
|------|------|
| MVP 6 维冻结 | ✅ 已冻结 |
| 扩展 4 维冻结 | ✅ 已冻结 |
| 校准 2+1 维冻结 | ✅ 已冻结 |
| 版本 | v1.0 |
| 下次允许变动 | 阶段 4 开始时 |
