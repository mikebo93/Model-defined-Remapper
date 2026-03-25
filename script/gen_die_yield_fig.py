"""
Generate die area vs defect yield figure (matplotlib version of PPTX slide).
Two wafers side-by-side: (a) large dies, (b) small dies — same defect positions.
"""

import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch

OUT = '/Users/mike/Desktop/Mike/VSCode/Model-defined-Remapper/image'

# ── Colors ─────────────────────────────────────────────────────────
GREEN_FILL = '#C8E6C8'
GREEN_EDGE = '#5AA85A'
RED_FILL = '#F2C4C4'
RED_EDGE = '#CC5555'
DEFECT_CLR = '#CC2222'
WAFER_FILL = '#F5F5F5'
WAFER_EDGE = '#888888'

# ── Generate defect positions (normalized, in unit circle) ─────────
rng = np.random.RandomState(42)
n_defects = 18
defects = []
while len(defects) < n_defects:
    r = math.sqrt(rng.random()) * 0.85
    theta = rng.random() * 2 * math.pi
    defects.append((r * math.cos(theta), r * math.sin(theta)))
defects = np.array(defects)


def draw_wafer_panel(ax, grid_n, defects, tag, title):
    """Draw one wafer with a grid_n x grid_n die layout."""
    # Wafer circle
    wafer = Circle((0, 0), 1.0, facecolor=WAFER_FILL, edgecolor=WAFER_EDGE,
                   linewidth=1.5, zorder=0)
    ax.add_patch(wafer)

    # Die grid: fit inside inscribed square of circle, no gap
    gap = 0.0
    inscribed_half = 1.0 / math.sqrt(2)
    total = 2 * inscribed_half
    die_size = total / grid_n
    origin = -total / 2

    n_good = 0
    n_bad = 0

    for row in range(grid_n):
        for col in range(grid_n):
            x0 = origin + col * (die_size + gap)
            y0 = origin + row * (die_size + gap)
            # Check all 4 corners inside wafer
            corners = [(x0, y0), (x0 + die_size, y0),
                       (x0, y0 + die_size), (x0 + die_size, y0 + die_size)]
            if not all(cx**2 + cy**2 <= 1.01 for cx, cy in corners):
                continue
            # Check if any defect hits this die
            hit = any(x0 <= dx <= x0 + die_size and y0 <= dy <= y0 + die_size
                      for dx, dy in defects)
            if hit:
                fc, ec = RED_FILL, RED_EDGE
                n_bad += 1
            else:
                fc, ec = GREEN_FILL, GREEN_EDGE
                n_good += 1
            rect = Rectangle((x0, y0), die_size, die_size,
                              facecolor=fc, edgecolor=ec, linewidth=0.8, zorder=1)
            ax.add_patch(rect)

    # Draw defect markers
    ax.scatter(defects[:, 0], defects[:, 1], c=DEFECT_CLR, s=12, zorder=2,
               edgecolors='none', alpha=0.9)

    # Formatting
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-1.35, 1.1)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)

    total_dies = n_good + n_bad
    yld = int(100 * n_good / total_dies) if total_dies > 0 else 0
    ax.text(0, -1.2, f'({tag}) {title} — {yld}% yield',
            fontsize=9, fontfamily='serif', ha='center', va='top')

    return n_good, n_bad


# ── Figure ─────────────────────────────────────────────────────────
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(5.0, 2.8))
fig.subplots_adjust(wspace=0.15)

draw_wafer_panel(ax1, 5, defects, 'a', 'Large dies')
draw_wafer_panel(ax2, 10, defects, 'b', 'Small dies')

fig.savefig(f'{OUT}/die_yield.pdf', bbox_inches='tight', pad_inches=0.02)
fig.savefig(f'{OUT}/die_yield.png', dpi=300, bbox_inches='tight', pad_inches=0.02)
print("Saved: die_yield.pdf / .png")
plt.close(fig)
