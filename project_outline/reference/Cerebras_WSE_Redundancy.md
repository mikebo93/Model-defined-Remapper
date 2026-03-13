# Cerebras WSE — Redundant Cores for Defect Tolerance

## Summary

Cerebras builds ~1-7% extra cores into each wafer-scale chip. Defective cores are replaced by nearby spares, and the routing fabric reconnects around them. The software sees a uniform mesh regardless of which cores are disabled.

| Chip | Process | Transistors | Physical Cores | Active Cores | Spare | SRAM | Die Size |
|------|---------|-------------|----------------|-------------|-------|------|----------|
| WSE-1 | TSMC 16nm | 1.2T | ~406K (est.) | 400,000 | ~1.5% | 18 GB | 46,225 mm² |
| WSE-2 | TSMC 7nm  | 2.6T | ~862K (est.) | 850,000 | ~1.5% | 40 GB | 46,225 mm² |
| WSE-3 | TSMC 5nm  | 4.0T | **970,000**  | **900,000** | **~7%** | 44 GB | 46,255 mm² |

Note: WSE-3 physical/active counts are explicit from Cerebras. WSE-1/WSE-2 physical counts are estimated from the ~1-1.5% spare figure reported for earlier generations.

---

## Sources & Where They Mention It

### 1. Cerebras Blog — "100x Defect Tolerance: How Cerebras Solved the Yield Problem"
- https://www.cerebras.ai/blog/100x-defect-tolerance-how-cerebras-solved-the-yield-problem
- **WSE-3 physical vs active:** *"970,000 physical cores with 900,000 active on our current shipping product"*
- **Core size vs GPU:** *"a defect in a WSE core would disable 0.05mm² of silicon while the same defect in an H100 disables ~6mm²"*
- **Yield claim:** *"Despite having built the world's largest chip, Cerebras enables 93% of their silicon area, which is higher than the leading GPU today."*
- **Routing around defects (section "The Routing Architecture"):** *"When a defect is detected, the system can automatically route around it using redundant communication pathways"* and *"a small reserve of spare cores that can be used to replace defective units"*

### 2. WikiChip Fuse — "A Look at Cerebras Wafer-Scale Engine"
- https://fuse.wikichip.org/news/3010/a-look-at-cerebras-wafer-scale-engine-half-square-foot-silicon-chip/2/
- **Spare percentage (section "How's the Yield?"):** *"Each wafer incorporates around 1-1.5% of additional AI cores for redundancy reasons."*
- **Replacement mechanism:** *"In an area affected by a defect, a local redundant core is used to replace the defective core. The local fabric is then appropriately reconnected using the redundant fabric links."*
- **When no defects:** *"When there are no defects in a certain area, the redundant cores are simply disabled."*
- **Sean Lie quote:** *"By using this technique, we can drive yield incredibly high and it's all transparent to the software since it shows up as a single uniformed fabric"*

### 3. Cerebras Press Release — WSE-1 Announcement
- https://www.cerebras.ai/press-release/cerebras-systems-unveils-the-industrys-first-trillion-transistor-chip
- **WSE-1 specs:** *"400,000 AI-optimized, no-cache, no-overhead, compute cores"* on 46,225 mm², 1.2T transistors, TSMC 16nm.

### 4. Cerebras Press Release — WSE-2 Announcement
- https://www.cerebras.ai/press-release/cerebras-systems-smashes-the-2-5-trillion-transistor-mark-with-new-second-generation-wafer-scale-engine
- **WSE-2 specs:** 850,000 cores, 2.6T transistors, TSMC 7nm, 40 GB SRAM.

### 5. Cerebras Press Release — WSE-3 Announcement
- https://www.cerebras.ai/press-release/cerebras-announces-third-generation-wafer-scale-engine
- **WSE-3 specs:** 900,000 cores (active), 4T transistors, TSMC 5nm, 44 GB SRAM.

### 6. Cerebras Product Page
- https://www.cerebras.ai/chip
- Lists WSE-3: 900,000 AI-optimized cores, 4T transistors, 44 GB SRAM, 46,255 mm².

### 7. Tom's Hardware — WSE-2 Coverage
- https://www.tomshardware.com/news/cerebras-wafer-scale-engine-2-worlds-largest-chip-7nm-850000-cores
- **WSE-2 details:** *"850,000 AI-optimized cores spread out over 46,225 mm² of silicon packed with 2.6 trillion transistors"*

### 8. Hot Chips 2024 — Cerebras Presentation (PDF)
- https://hc2024.hotchips.org/assets/program/conference/day2/72_HC2024.Cerebras.Sean.v03.final.pdf
- Official presentation by Sean Lie. Should contain detailed yield/redundancy architecture slides.

### 9. arXiv — Comparison of Cerebras with NVIDIA GPU Systems
- https://arxiv.org/html/2503.11698v1
- Academic comparison paper; mentions fault tolerance via fine-grained sparing and redundant mesh routing.

---

## Key Takeaway for Paper

Cerebras is the most extreme example of on-chip defect tolerance through redundancy: the WSE-3 has 970K physical cores but ships with only 900K active (~7% spare). Defective cores are locally replaced and the 2D mesh fabric reroutes around them — conceptually the same problem as the virtual-to-physical remapping this paper addresses, but at a finer granularity and with a proprietary fixed strategy rather than a general-purpose optimizer.
