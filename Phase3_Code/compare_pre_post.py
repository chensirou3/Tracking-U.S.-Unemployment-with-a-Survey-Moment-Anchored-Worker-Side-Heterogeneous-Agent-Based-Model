import json
print('=== PRE vs POST CALIBRATION ===')
print('PRE-CALIBRATION (default params):')
print('  UR RMSE = 3.98 pp')
print('  UR Corr = 0.773')
print('  UR MAE  = 2.97 pp')
with open('Phase3_Output/phase6/calibration_results.json') as f:
    results = json.load(f)
best = results[0]
print()
print('POST-CALIBRATION (baseline):')
ur = best['train_comp_avg']['ur'] * 100
lfpr = best['train_comp_avg']['lfpr'] * 100
print(f'  Train UR RMSE  = {ur:.2f} pp')
print(f'  Train LFPR RMSE= {lfpr:.2f} pp')
print(f'  Train Total    = {best["train_mean"]:.4f}')
print(f'  Val Total      = {best["val_mean"]:.4f}')
print(f'  Stable         = {best["stable"]}')
print()
pre = 3.98
print(f'UR RMSE improvement: {pre:.2f} -> {ur:.2f} pp ({(1-ur/pre)*100:.0f}% reduction)')
