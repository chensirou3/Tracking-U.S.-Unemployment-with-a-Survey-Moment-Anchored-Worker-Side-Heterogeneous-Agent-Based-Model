import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = json.load(open('正式撰写/fix6.3/calibration_results.json', encoding='utf-8'))
for v, info in d.items():
    print(f"{v:20s}  n_draws={info['n_draws']}  top5_idx={info['top5_idx']}  "
          f"top1_mean={info['top5_mean'][0]:.4f}  top1_std={info['top5_std'][0]:.4f}")
