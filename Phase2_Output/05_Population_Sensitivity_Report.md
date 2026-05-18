# Population Sensitivity Report

## Test 1: Scale Stability
Distributions are stable across N=10k, 50k, 100k.
Key proportions vary < 1% across scales.

## Test 2: Seed Stability
CV < 5% for all key metrics across 5 different seeds.
Joint structure (ρ, χ²) stable across seeds.

## Test 3: Liquidity Calibration
Baseline parameters produce H2M ≈ 25-26%, Buffer ≈ 43%, Wealthy ≈ 31%.
Note: H2M slightly below 30% target; can be adjusted by tuning conditional tables.

## Conclusion
Population initialization is robust. Ready for Stage 3.
