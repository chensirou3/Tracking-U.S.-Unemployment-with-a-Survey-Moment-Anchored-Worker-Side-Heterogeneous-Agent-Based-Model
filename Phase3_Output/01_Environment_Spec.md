# Environment Specification

> Phase 3 — Main Model Core Engine

## 环境变量

| 变量 | 含义 | 基线值 | 衰退峰值 | 来源 |
|------|------|--------|---------|------|
| market_tightness | 劳动市场紧张度 (V/U proxy) | 1.0 | 0.6 | 外生路径 |
| separation_rate | 月度裁员/分离率 | 0.012 | 0.027 | 外生路径 |
| income_growth_bg | 背景收入增长率/月 | 0.002 | -0.003 | 外生路径 |
| borrowing_rate | 借贷利率/年 | 0.05 | 0.08 | 外生路径 |

## 情景

| 情景 | 说明 |
|------|------|
| baseline | 稳态经济，微弱正弦波动 |
| recession | 前36月平稳 → t=36开始衰退 → t=48峰值 → t=60-84缓慢恢复 |
| constant | 全平路径（调试用） |

## 接口

```python
env = Environment(T=120, scenario='baseline', seed=42)
env_t = env.get(t)  # returns dict with 4 keys
```
