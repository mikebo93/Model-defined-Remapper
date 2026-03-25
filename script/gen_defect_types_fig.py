"""
Generate a figure showing different types of wafer defect patterns.
Based on wafer map classification (Xu et al. 2022, WM-811K dataset).
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

OUT = '/Users/mike/Desktop/Mike/VSCode/Model-defined-Remapper/image'
rng = np.random.default_rng(42)


def wafer_circle(ax, title, tag):
    """Draw a wafer outline and set up the axis."""
    circle = plt.Circle((0, 0), 1.0, fill=True, facecolor='#F5F5F5',
                         edgecolor='#888888', linewidth=1.5)
    ax.add_patch(circle)
    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-1.1, 1.15)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_title(f'({tag}) {title}', fontsize=9, fontfamily='serif', pad=2)


def scatter_defects(ax, x, y, color='#CC2222', size=8, alpha=0.7):
    ax.scatter(x, y, c=color, s=size, alpha=alpha, edgecolors='none', zorder=3)


def gen_random(n=120):
    """Random defects — uniform across wafer."""
    pts = []
    while len(pts) < n:
        x, y = rng.uniform(-0.95, 0.95, 2)
        if x**2 + y**2 < 0.9:
            pts.append((x, y))
    pts = np.array(pts)
    return pts[:, 0], pts[:, 1]


def gen_edge_ring(n=150):
    """Edge-ring defects — concentrated near wafer periphery."""
    pts = []
    while len(pts) < n:
        theta = rng.uniform(0, 2 * np.pi)
        r = 0.75 + rng.normal(0, 0.08)
        r = np.clip(r, 0.55, 0.95)
        x, y = r * np.cos(theta), r * np.sin(theta)
        if x**2 + y**2 < 0.95:
            pts.append((x, y))
    pts = np.array(pts)
    return pts[:, 0], pts[:, 1]


def gen_center(n=100):
    """Center defects — concentrated at wafer center (CMP pressure)."""
    pts = []
    while len(pts) < n:
        r = abs(rng.normal(0, 0.2))
        r = np.clip(r, 0, 0.45)
        theta = rng.uniform(0, 2 * np.pi)
        x, y = r * np.cos(theta), r * np.sin(theta)
        pts.append((x, y))
    pts = np.array(pts)
    return pts[:, 0], pts[:, 1]


def gen_scratch(n=80):
    """Scratch defects — along a line (mechanical handling), offset from center."""
    t = rng.uniform(-0.85, 0.85, n)
    angle = 0.6  # radians
    # Offset perpendicular to the scratch direction
    perp_x, perp_y = -np.sin(angle), np.cos(angle)
    offset = 0.25
    x = t * np.cos(angle) + offset * perp_x + rng.normal(0, 0.03, n)
    y = t * np.sin(angle) + offset * perp_y + rng.normal(0, 0.03, n)
    mask = x**2 + y**2 < 0.9
    return x[mask], y[mask]


def gen_local(n=60):
    """Local defects — cluster in a localized region (process excursion)."""
    cx, cy = 0.3, -0.25  # cluster center
    x = rng.normal(cx, 0.12, n)
    y = rng.normal(cy, 0.12, n)
    mask = x**2 + y**2 < 0.9
    return x[mask], y[mask]


def gen_donut(n=120):
    """Donut defects — ring pattern between center and edge."""
    pts = []
    while len(pts) < n:
        theta = rng.uniform(0, 2 * np.pi)
        r = 0.45 + rng.normal(0, 0.07)
        r = np.clip(r, 0.3, 0.6)
        x, y = r * np.cos(theta), r * np.sin(theta)
        pts.append((x, y))
    pts = np.array(pts)
    return pts[:, 0], pts[:, 1]


# ── Create figure ───────────────────────────────────────────────────
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']

fig, axes = plt.subplots(2, 3, figsize=(5.5, 3.8))
fig.subplots_adjust(hspace=0.02, wspace=0.1)

patterns = [
    ("Random", gen_random),
    ("Edge-Ring", gen_edge_ring),
    ("Center", gen_center),
    ("Scratch", gen_scratch),
    ("Local", gen_local),
    ("Donut", gen_donut),
]

tags = 'abcdef'
for ax, (name, gen_fn), tag in zip(axes.flatten(), patterns, tags):
    wafer_circle(ax, name, tag)
    x, y = gen_fn()
    scatter_defects(ax, x, y)

fig.savefig(f'{OUT}/defect_types.pdf', bbox_inches='tight', pad_inches=0.02)
fig.savefig(f'{OUT}/defect_types.png', dpi=300, bbox_inches='tight', pad_inches=0.02)
print(f"Saved: defect_types.pdf / .png")
plt.close(fig)
