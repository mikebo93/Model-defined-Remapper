"""
Monte Carlo simulation: distribution of max defect-free square submesh
on a 1000x1000 wafer-scale mesh at various defect rates.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from time import time

# ── Parameters ──────────────────────────────────────────────────────
W = 1000                          # wafer mesh side length
DEFECT_RATES = [0.01, 0.02, 0.04, 0.06, 0.08, 0.10]
N_TRIALS = 200                    # trials per defect rate
SEED = 42

# ── Largest defect-free square via DP (maximal square) ──────────────
def largest_defect_free_square(grid_healthy):
    """
    Given a boolean 2D array (True = healthy), return the side length
    of the largest all-True square subregion.  O(W^2) time and space.
    """
    H, W_ = grid_healthy.shape
    # dp[i,j] = side length of largest square with bottom-right at (i,j)
    dp = np.zeros((H, W_), dtype=np.int32)
    dp[0, :] = grid_healthy[0, :]
    dp[:, 0] = grid_healthy[:, 0]
    for i in range(1, H):
        for j in range(1, W_):
            if grid_healthy[i, j]:
                dp[i, j] = min(dp[i-1, j], dp[i, j-1], dp[i-1, j-1]) + 1
            # else dp[i,j] stays 0
    return int(dp.max())

# Numba-accelerated version if available
try:
    from numba import njit

    @njit
    def _largest_square_numba(healthy, H, W_):
        dp = np.zeros((H, W_), dtype=np.int32)
        for j in range(W_):
            dp[0, j] = 1 if healthy[0, j] else 0
        for i in range(H):
            dp[i, 0] = 1 if healthy[i, 0] else 0
        best = 0
        for i in range(H):
            if dp[i, 0] > best:
                best = dp[i, 0]
        for j in range(W_):
            if dp[0, j] > best:
                best = dp[0, j]
        for i in range(1, H):
            for j in range(1, W_):
                if healthy[i, j]:
                    v = dp[i-1, j]
                    if dp[i, j-1] < v:
                        v = dp[i, j-1]
                    if dp[i-1, j-1] < v:
                        v = dp[i-1, j-1]
                    dp[i, j] = v + 1
                    if dp[i, j] > best:
                        best = dp[i, j]
        return best

    def largest_square_fast(grid_healthy):
        H, W_ = grid_healthy.shape
        return int(_largest_square_numba(grid_healthy, H, W_))

    # warm up JIT
    _test = np.ones((10, 10), dtype=np.bool_)
    largest_square_fast(_test)
    find_largest = largest_square_fast
    print("Using numba-accelerated DP")
except ImportError:
    find_largest = largest_defect_free_square
    print("Numba not available, using pure numpy DP (slower)")

# ── Run Monte Carlo ─────────────────────────────────────────────────
rng = np.random.default_rng(SEED)
results = {}  # {p: [list of max square side lengths]}

for p in DEFECT_RATES:
    t0 = time()
    sizes = []
    for trial in range(N_TRIALS):
        # Generate defect map: True = healthy, False = defective
        healthy = rng.random((W, W)) >= p
        s = find_largest(healthy)
        sizes.append(s)
        if (trial + 1) % 50 == 0:
            elapsed = time() - t0
            print(f"  p={p:.0%}: trial {trial+1}/{N_TRIALS}  "
                  f"({elapsed:.1f}s, mean so far: {np.mean(sizes):.1f})")
    results[p] = sizes
    elapsed = time() - t0
    print(f"p={p:.0%}: mean={np.mean(sizes):.1f}, "
          f"median={np.median(sizes):.1f}, "
          f"std={np.std(sizes):.1f}, "
          f"min={np.min(sizes)}, max={np.max(sizes)}  "
          f"[{elapsed:.1f}s]")

# ── Also compute theoretical s* for comparison ──────────────────────
print("\n── Comparison: simulated vs theoretical ──")
print(f"{'p':>6}  {'theory s*':>10}  {'sim mean':>10}  {'sim median':>10}  "
      f"{'utilization':>12}")
for p in DEFECT_RATES:
    s_theory = np.sqrt(2 * np.log(W) / p)
    s_sim_mean = np.mean(results[p])
    s_sim_median = np.median(results[p])
    util = (s_sim_mean / W) ** 2 * 100
    print(f"{p:>6.0%}  {s_theory:>10.1f}  {s_sim_mean:>10.1f}  "
          f"{s_sim_median:>10.1f}  {util:>11.3f}%")

# ── Plot: histogram per defect rate ─────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(12, 7), constrained_layout=True)
axes = axes.flatten()

# Colorblind-friendly palette (Wong)
colors = ['#0072B2', '#E69F00', '#009E73', '#D55E00', '#CC79A7', '#56B4E9']

for idx, p in enumerate(DEFECT_RATES):
    ax = axes[idx]
    data = results[p]
    s_theory = np.sqrt(2 * np.log(W) / p)

    ax.hist(data, bins=range(min(data), max(data) + 2), color=colors[idx],
            edgecolor='white', linewidth=0.5, alpha=0.85)
    ax.axvline(np.mean(data), color='black', linestyle='-', linewidth=1.5,
               label=f'mean = {np.mean(data):.1f}')
    ax.axvline(s_theory, color='red', linestyle='--', linewidth=1.5,
               label=f'theory = {s_theory:.1f}')
    ax.set_title(f'p = {p:.0%}', fontsize=12, fontweight='bold')
    ax.set_xlabel('Max defect-free square side length', fontsize=9)
    ax.set_ylabel('Count', fontsize=9)
    ax.legend(fontsize=8, loc='upper right')
    ax.tick_params(labelsize=8)

fig.suptitle(f'Distribution of max defect-free square submesh on {W}x{W} mesh\n'
             f'({N_TRIALS} Monte Carlo trials per defect rate)',
             fontsize=13, fontweight='bold')

out_base = '/Users/mike/Desktop/Mike/VSCode/Model-defined-Remapper/image'
fig.savefig(f'{out_base}/montecarlo_meshsize.pdf', bbox_inches='tight')
fig.savefig(f'{out_base}/montecarlo_meshsize.png', dpi=300, bbox_inches='tight')
print(f"\nSaved: montecarlo_meshsize.pdf / .png")

# ── Plot 2: combined overlay for paper figure ───────────────────────
fig2, ax2 = plt.subplots(figsize=(7, 4), constrained_layout=True)

for idx, p in enumerate(DEFECT_RATES):
    data = results[p]
    bins = range(min(data), max(data) + 2)
    ax2.hist(data, bins=bins, color=colors[idx], alpha=0.6,
             edgecolor='white', linewidth=0.3,
             label=f'p = {p:.0%} (mean={np.mean(data):.0f})')

ax2.set_xlabel('Max defect-free square side length', fontsize=11)
ax2.set_ylabel('Count', fontsize=11)
ax2.set_title(f'Max defect-free submesh on {W}$\\times${W} mesh '
              f'({N_TRIALS} trials)', fontsize=12)
ax2.legend(fontsize=9)
ax2.tick_params(labelsize=9)

# Add utilization annotation
ax2.annotate(f'At p=1%, mean max square ≈ {np.mean(results[0.01]):.0f}×'
             f'{np.mean(results[0.01]):.0f}\n'
             f'= {(np.mean(results[0.01])/W)**2*100:.2f}% utilization',
             xy=(np.mean(results[0.01]), 0), xytext=(np.mean(results[0.01])+5, N_TRIALS*0.3),
             fontsize=9, arrowprops=dict(arrowstyle='->', color='black'),
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', edgecolor='gray'))

fig2.savefig(f'{out_base}/montecarlo_meshsize_combined.pdf', bbox_inches='tight')
fig2.savefig(f'{out_base}/montecarlo_meshsize_combined.png', dpi=300, bbox_inches='tight')
print(f"Saved: montecarlo_meshsize_combined.pdf / .png")

plt.close('all')
