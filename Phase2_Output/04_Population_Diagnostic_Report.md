# Population Diagnostic Report

N = 100000


## 1. Marginal Distributions

### Age: <40=0.277(target:0.277), 40-60=0.391(0.391), >60=0.332(0.332)
  Edu=HS: 0.113
  Edu=SomeCol: 0.332
  Edu=College+: 0.554
  Employment E: 0.586 (target:0.6) ✅
  Employment U: 0.039 (target:0.04) ✅
  Employment N: 0.375 (target:0.36) ✅
  Housing Renter-Mobile: 0.112 (target:0.12)
  Housing Renter-Stable: 0.192 (target:0.2)
  Housing Owner-Low: 0.463 (target:0.45)
  Housing Owner-High: 0.234 (target:0.23)
  Total Owner: 0.697 (target: ~0.66-0.68)
  Liquidity H2M: 0.255 (target:0.3)
  Liquidity Buffer: 0.432 (target:0.45)
  Liquidity Wealthy: 0.313 (target:0.25)
  Consumption Saver: 0.305
  Consumption Smoother: 0.400
  Consumption Spender: 0.296

### Continuous Variables

  income_expectation: mean=0.0204, std=0.0384, min=-0.1782, max=0.1732 | target: mean~0.03, std~0.04
  income_uncertainty: mean=0.0398, std=0.0114, min=0.0200, max=0.1447 | target: mean~0.03
  labor_fragility: mean=0.3289, std=0.1855, min=0.0000, max=1.0000 | target: mean~0.30, [0,1]
  cash_buffer_months: mean=5.2215, std=5.2754, min=0.0000, max=27.4782 | target: H2M~0.5, Buffer~3, Wealthy~12
  search_intensity: mean=0.3844, std=2.6305, min=0.0000, max=40.0000 | target: U>0, E=0
  mobility_friction: mean=0.5488, std=0.2424, min=0.0000, max=1.0000 | target: Renter<Owner
  household_income: mean=45.4680, std=23.3820, min=5.0000, max=225.1611 | target: mean~50 ($k)
  reservation_wage: mean=1.4589, std=0.6652, min=0.5000, max=5.0000 | target: mean~1.0, [0.5,5.0]
  mpc_positive: mean=0.4485, std=0.2632, min=0.0100, max=0.9900 | target: mean~0.45
  mpc_negative: mean=0.3149, std=0.2093, min=0.0100, max=0.9900 | target: mean~0.30

## 2. Joint Structure Validation

  R1: fragility × income_exp: ρ=-0.279, p=0.00e+00 ✅
  R2: liquidity × consumption: χ²=24103.9, p=0.00e+00 ✅
      Cross-table:
[[ 2510  7629 15372]
 [10850 21308 10994]
 [17119 11027  3191]]
  R3: Owner flex=-0.533, Renter flex=0.569 ✅
  R4: housing × liquidity: χ²=5483.5, p=0.00e+00 ✅
  R5: Search: E=0.00, U=9.88, N=0.00 ✅

## 3. Illegal Value Checks

  ages in [18,85]: ✅ PASS
  employment in {0,1,2}: ✅ PASS
  liquidity in {0,1,2}: ✅ PASS
  housing in {0,1,2,3}: ✅ PASS
  income_exp no NaN: ✅ PASS
  fragility in [0,1]: ✅ PASS
  cash_buffer >= 0: ✅ PASS
  search_int >= 0: ✅ PASS
  resv_wage in [0.5,5]: ✅ PASS
  mpc_pos in (0,1): ✅ PASS
  mpc_neg in (0,1): ✅ PASS
  E agents: search=0: ✅ PASS
  N agents: search=0: ✅ PASS
  E/N agents: unemp_dur=0: ✅ PASS

## Summary

All illegal value checks passed: ✅
Population ready for Stage 3: ✅