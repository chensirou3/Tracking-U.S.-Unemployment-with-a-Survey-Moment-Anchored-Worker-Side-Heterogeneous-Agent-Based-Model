"""Smoke test for fix6.3 — confirm flatten dispatch works for each variant."""
import sys, time
sys.path.insert(0, '.')
sys.path.insert(0, '正式撰写/fix6.3')
import run_fix6_3_calibrate as m
from Phase3_Code.environment_real import RealEnvironment

env = RealEnvironment(data_dir='Phase3_Data')
test_vec = (m.LOWS + m.HIGHS) / 2  # midpoint of param space
for variant in m.VARIANT_SPEC.keys():
    t0 = time.perf_counter()
    hist = m.run_one(test_vec, variant, 42, env)
    total, comp = m.compute_train_loss(hist)
    flatten = m.VARIANT_SPEC[variant]['flatten']
    print(f'{variant:20s} flatten={str(flatten):<45s} total={total:.4f} ur={comp["ur"]:.4f} runtime={time.perf_counter()-t0:.1f}s', flush=True)
print('smoke test OK')
