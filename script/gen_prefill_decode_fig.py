"""
Generate prefill vs decode illustration figure.
Prefill: all input tokens processed at once, load W once → GEMM (compute-bound)
Decode: one token per step, must reload W every step → GEMV (memory-bound)
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patches as mpatches
import numpy as np

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.5, 3.6), gridspec_kw={'width_ratios': [1, 1.35]})
fig.subplots_adjust(wspace=0.12)

# Common settings
token_h = 0.35
token_w = 0.44
ylim = (-0.1, 3.15)

def draw_token(ax, x, y, text, color='#EF9A9A', textcolor='black', alpha=1.0, w=token_w, h=token_h):
    rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                           boxstyle="round,pad=0.03", facecolor=color,
                           edgecolor='gray', linewidth=0.7, alpha=alpha)
    ax.add_patch(rect)
    ax.text(x, y, text, ha='center', va='center', fontsize=5.5,
            color=textcolor, fontweight='bold', alpha=alpha)

def draw_block(ax, x, y, w, h, text, color, textcolor='black', fontsize=7, ls='-'):
    rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                           boxstyle="round,pad=0.04", facecolor=color,
                           edgecolor='#555555', linewidth=1.0, linestyle=ls)
    ax.add_patch(rect)
    ax.text(x, y, text, ha='center', va='center', fontsize=fontsize,
            color=textcolor, fontweight='bold')

def draw_arrow(ax, x, y1, y2, color='#555555'):
    ax.annotate('', xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.1))

# ============================================================
# (a) Prefill Phase — load W once, multiply with all tokens
# ============================================================
ax1.set_title('(a) Prefill Phase', fontsize=9, fontweight='bold', pad=8)

tokens = ['The', 'cat', 'sat', 'on', 'the', 'mat']
n = len(tokens)
spacing = 0.52
total_tw = (n - 1) * spacing
cx1 = 2.0  # center x
x_start = cx1 - total_tw / 2
xs = [x_start + i * spacing for i in range(n)]

# Row: input tokens
token_y = 2.6
for x, t in zip(xs, tokens):
    draw_token(ax1, x, token_y, t, color='#EF9A9A')

# Brace under all tokens
brace_y = token_y - token_h/2 - 0.12
ax1.annotate('', xy=(xs[0] - token_w/2, brace_y),
             xytext=(xs[-1] + token_w/2, brace_y),
             arrowprops=dict(arrowstyle='|-|', color='#C62828', lw=0.8))
ax1.text(cx1, brace_y - 0.1, f'{n} tokens (all at once)',
         ha='center', va='top', fontsize=5.5, color='#C62828', style='italic')

# Arrow down
draw_arrow(ax1, cx1, brace_y - 0.22, 1.72)

# Weight matrix block (loaded once)
draw_block(ax1, cx1, 1.5, 3.0, 0.38, r'Load $W$ once', '#BBDEFB', fontsize=7)

# Arrow down
draw_arrow(ax1, cx1, 1.28, 0.82)

# GEMM box
draw_block(ax1, cx1, 0.6, 3.0, 0.38,
           r'GEMM: $W_{E \times F} \times A_{E \times L}$',
           '#C8E6C9', fontsize=7)

# Label below
ax1.text(cx1, 0.28, 'Compute-bound: W reused across L tokens',
         ha='center', va='top', fontsize=5.5, color='#2E7D32', style='italic')

ax1.set_xlim(0.1, 3.9)
ax1.set_ylim(*ylim)
ax1.set_aspect('equal')
ax1.axis('off')

# ============================================================
# (b) Decode Phase — load W every step, multiply with 1 token
# ============================================================
ax2.set_title('(b) Decode Phase', fontsize=9, fontweight='bold', pad=8)

# Show 3 decode steps side by side
decode_tokens = ['is', 'a', '...']
n_steps = len(decode_tokens)
step_spacing = 1.8
total_sw = (n_steps - 1) * step_spacing
cx2 = 2.8
step_xs = [cx2 - total_sw/2 + i * step_spacing for i in range(n_steps)]

for si, (sx, tok) in enumerate(zip(step_xs, decode_tokens)):
    step_label = f'Step {si+1}' if si < 2 else '...'

    # Step label at top
    ax2.text(sx, 2.95, step_label, ha='center', va='center',
             fontsize=6, color='#555555', fontweight='bold')

    # Single token
    token_y2 = 2.55
    draw_token(ax2, sx, token_y2, tok, color='#EF5350', textcolor='white')

    # Arrow down
    draw_arrow(ax2, sx, token_y2 - token_h/2 - 0.05, 1.72)

    # Load W block (repeated each step)
    draw_block(ax2, sx, 1.5, 1.5, 0.38, r'Load $W$', '#FFCDD2', fontsize=6.5)

    # Arrow down
    draw_arrow(ax2, sx, 1.28, 0.82)

    # GEMV box
    draw_block(ax2, sx, 0.6, 1.5, 0.38,
               r'GEMV: $W \times \mathbf{x}$',
               '#FFE0B2', fontsize=6.5)

ax2.text(cx2, 0.25, 'Memory-bound: W reloaded every step, used only once',
         ha='center', va='top', fontsize=5.5, color='#E65100', style='italic')

# Dashed arrows between steps to show sequential nature
for i in range(n_steps - 1):
    mid_x = (step_xs[i] + step_xs[i+1]) / 2
    ax2.annotate('', xy=(step_xs[i+1] - 0.8, 0.6),
                 xytext=(step_xs[i] + 0.8, 0.6),
                 arrowprops=dict(arrowstyle='->', color='#888888',
                                 lw=1.0, linestyle='dashed'))

ax2.set_xlim(0.2, 5.4)
ax2.set_ylim(*ylim)
ax2.set_aspect('equal')
ax2.axis('off')

plt.savefig('../image/prefill_decode.pdf', bbox_inches='tight', dpi=300)
plt.savefig('../image/prefill_decode.png', bbox_inches='tight', dpi=300)
print('Saved to ../image/prefill_decode.pdf and .png')
