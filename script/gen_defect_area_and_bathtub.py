"""
Generate two figures for §2.1:
  (b) Defect rate vs. max defect-free mesh area (box plot from Monte Carlo data)
  (c) Bathtub curve (failure rate over device lifetime)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from time import time

OUT = '/Users/mike/Desktop/Mike/VSCode/Model-defined-Remapper/image'

# ══════════════════════════════════════════════════════════════════════
# Panel (b): Defect rate vs. max defect-free mesh area
# ══════════════════════════════════════════════════════════════════════

# ── Re-run Monte Carlo (or load cached) ─────────────────────────────
W = 1000
DEFECT_RATES = [0.01, 0.02, 0.04, 0.06, 0.08, 0.10]
N_TRIALS = 200
SEED = 42

def largest_defect_free_square(healthy):
    H, W_ = healthy.shape
    dp = np.zeros((H, W_), dtype=np.int32)
    dp[0, :] = healthy[0, :]
    dp[:, 0] = healthy[:, 0]
    for i in range(1, H):
        for j in range(1, W_):
            if healthy[i, j]:
                dp[i, j] = min(dp[i-1, j], dp[i, j-1], dp[i-1, j-1]) + 1
    return int(dp.max())

rng = np.random.default_rng(SEED)
results = {}

for p in DEFECT_RATES:
    t0 = time()
    sizes = []
    for trial in range(N_TRIALS):
        healthy = rng.random((W, W)) >= p
        s = largest_defect_free_square(healthy)
        sizes.append(s)
        if (trial + 1) % 50 == 0:
            print(f"  p={p:.0%}: trial {trial+1}/{N_TRIALS} ({time()-t0:.1f}s)")
    results[p] = np.array(sizes)
    print(f"p={p:.0%}: mean side={np.mean(sizes):.1f}, "
          f"mean area={np.mean(np.array(sizes)**2):.0f}  [{time()-t0:.1f}s]")

# ── Plot: box plot of area ──────────────────────────────────────────
fig, ax = plt.subplots(figsize=(5.5, 3.5), constrained_layout=True)

# Convert side lengths to areas
areas = [results[p] ** 2 for p in DEFECT_RATES]
labels = [f'{p:.0%}' for p in DEFECT_RATES]

bp = ax.boxplot(areas, labels=labels, patch_artist=True, widths=0.5,
                medianprops=dict(color='black', linewidth=1.5),
                flierprops=dict(marker='o', markersize=3, alpha=0.5))

colors = ['#0072B2', '#E69F00', '#009E73', '#D55E00', '#CC79A7', '#56B4E9']
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

# Add mean markers
means = [np.mean(a) for a in areas]
ax.scatter(range(1, len(DEFECT_RATES)+1), means, color='red', marker='D',
           s=30, zorder=5, label='Mean')

# Annotate key point
ax.annotate(f'Mean: {means[0]:.0f} cores\n'
            f'({np.mean(results[0.01]):.0f}$\\times${np.mean(results[0.01]):.0f})',
            xy=(1, means[0]), xytext=(2.3, means[0] + 300),
            fontsize=8, arrowprops=dict(arrowstyle='->', color='black', lw=0.8),
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                      edgecolor='gray', alpha=0.9))

# Reference lines for workload mesh needs
ax.axhline(y=360**2, color='gray', linestyle=':', linewidth=1, alpha=0.7)
ax.text(6.55, 360**2, 'Decode need\n(360$\\times$360)', fontsize=7,
        va='center', ha='left', color='gray')

ax.set_xlabel('Defect rate', fontsize=11)
ax.set_ylabel('Max defect-free square area (cores)', fontsize=11)
ax.set_title(f'Largest defect-free submesh on {W}$\\times${W} wafer',
             fontsize=11, fontweight='bold')
ax.legend(fontsize=8, loc='upper right')
ax.tick_params(labelsize=9)

# Use log scale for y to show the gap with workload needs
ax.set_yscale('log')
ax.set_ylim(50, 200000)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f'{x:,.0f}'))

fig.savefig(f'{OUT}/defect_vs_area.pdf', bbox_inches='tight')
fig.savefig(f'{OUT}/defect_vs_area.png', dpi=300, bbox_inches='tight')
print(f"\nSaved: defect_vs_area.pdf / .png")
plt.close(fig)


# ══════════════════════════════════════════════════════════════════════
# Panel (c): Bathtub curve
# ══════════════════════════════════════════════════════════════════════

fig2, ax2 = plt.subplots(figsize=(5.5, 3), constrained_layout=True)

# Synthetic bathtub curve shape
t = np.linspace(0, 10, 1000)

# Infant mortality (decreasing Weibull-like)
infant = 2.0 * np.exp(-1.5 * t)
# Wear-out (increasing Weibull-like) — steep rise for visual emphasis
wearout = 0.01 * np.exp(1.8 * (t - 7))
wearout = np.clip(wearout, 0, 5.0)
# Constant base rate during useful life
base = 0.1 * np.ones_like(t)
# Combined
failure_rate = infant + base + wearout

ax2.plot(t, failure_rate, color='#0072B2', linewidth=2.5)
ax2.fill_between(t, failure_rate, alpha=0.08, color='#0072B2')

# Phase boundaries
t_early = 2.0
t_wearout = 7.0
ax2.axvline(t_early, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)
ax2.axvline(t_wearout, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)

# Phase labels
ax2.text(t_early / 2, 2.5, 'Early\nfailure', ha='center', va='center',
         fontsize=9, color='#555555', fontstyle='italic')
ax2.text((t_early + t_wearout) / 2, 2.5, 'Useful life\n(constant rate)',
         ha='center', va='center', fontsize=9, color='#555555',
         fontstyle='italic')
ax2.text((t_wearout + 10) / 2, 2.5, 'Wear-out\n(aging)',
         ha='center', va='center', fontsize=9, color='#555555',
         fontstyle='italic')

ax2.set_xlabel('Device lifetime', fontsize=11)
ax2.set_ylabel('Failure rate', fontsize=11)
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 3.5)
ax2.set_xticks([])
ax2.set_yticks([])
# Remove top/right spines
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

fig2.savefig(f'{OUT}/bathtub_curve.pdf', bbox_inches='tight')
fig2.savefig(f'{OUT}/bathtub_curve.png', dpi=300, bbox_inches='tight')
print(f"Saved: bathtub_curve.pdf / .png")
plt.close(fig2)
