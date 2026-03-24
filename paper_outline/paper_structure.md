# Paper Structure: Defect-Tolerant Wafer-Scale NoC Remapping for Disaggregated AI Inference (MICRO 2026)

> Target: 11 pages, double-column, double-blind.
> MICRO recommended flow: Introduction → Background → Design → Implementation → Evaluation → Related Work → Conclusion.

---

## 1. Introduction (~1.5 pages)

**P1 — The setting: wafer-scale mesh for AI inference.**
Wafer-scale 2D mesh architectures (Cerebras WSE: ~900K cores, chiplet interposers) have emerged as the dominant substrate for large-scale AI workloads. Their planar, nearest-neighbor interconnect scales naturally with silicon area and supports the structured communication patterns (systolic data flow, broadcast/reduce) that AI inference demands. As model sizes grow, so does the pressure to use every available core efficiently.

**P2 — The workload insight: right-sized mesh matters.**
LLM inference is not monolithic — it decomposes into two phases with fundamentally different characteristics. Prefill processes the full input prompt via GEMM (compute-bound, high arithmetic intensity); decode generates tokens one at a time via GEMV (memory-bandwidth-bound, low arithmetic intensity). Crucially, optimal performance requires *right-sized* mesh partitions for each phase — WaferLLM \cite{he2025waferllm} demonstrates on Cerebras hardware that decode throughput can actually *decrease* when scaling to more cores, because communication overhead outweighs the computational benefit. The disaggregated inference trend \cite{zhong2024distserve, patel2024splitwise} formalizes this by separating prefill and decode onto differently-sized hardware partitions.

**P3 — The defect problem: you can't get the mesh you need.**
But manufacturing defects are inevitable at wafer scale. Even at a modest 1% defect rate, the largest contiguous defect-free mesh on a 750×750 wafer covers only ~0.23% of available cores (§2.1). Defects fragment the physical substrate — the right-sized mesh for a given workload may simply not exist as a contiguous region.

**P4 — Why current solutions aren't enough.**
Industry addresses defects through yield binning (NVIDIA, AMD), edge discard (Tilera), and spare-core remapping (Cerebras, Tesla Dojo). Cerebras's approach is the most sophisticated: a proprietary algorithm routes around defects to expose a regular 2D mesh to software \cite{cerebras2025sigops, luczynski2024reduce}. However, the algorithm is undisclosed and cannot be reproduced or extended. Moreover, it only restores regularity — it does not optimize for workload-specific communication patterns, and it conceals redundant resources (spare cores, diagonal links) that could improve performance rather than merely restoring a regular topology.

**P5 — Our approach.**
Given that inevitable defects cause serious mesh performance degradation (§2.1) and that AI inference workloads have distinct communication requirements per phase (§2.2), we propose a remapping framework that addresses the problem at three levels:
1. **Remap over defective mesh to expose regular virtual topology with deadlock-free routing.** The remapper maps a virtual regular mesh onto all healthy nodes of a defective physical substrate — recovering usable area that discard-based approaches abandon. Crucially, the resulting irregular physical paths are guaranteed deadlock-free via a submesh-hierarchy routing scheme, without which any remapping over irregular topology is unusable in practice.
2. **Optimize remapping for workload communication patterns.** Rather than a topology-only mapping, the remapper incorporates workload-specific cost functions — minimizing hop stretch along systolic data-flow edges for GEMM (prefill) and broadcast/reduce tree depth for GEMV (decode). This enables right-sized, communication-efficient virtual partitions for each inference phase.
3. **Exploit redundant resources to further mitigate remapping overhead.** Current approaches hide spare cores, extra links (e.g., diagonal connections), and additional virtual channels behind a regular facade. Our remapper instead exposes and utilizes these resources — diagonal links as routing shortcuts to reduce hop count, spare cores as additional compute capacity, and extra channels for routing flexibility — turning redundancy overhead into a performance advantage.

**P6 — Contributions:**
1. A hierarchical virtual-to-physical topology remapping framework that scales to 512×512 meshes, with provably deadlock-free routing on arbitrary post-remapping topologies via submesh hierarchy routing (ascend-then-descend, requiring only ≥2 virtual channels).
2. A workload-aware cost model that optimizes remapping for disaggregated AI inference — separately tuned for prefill (GEMM) and decode (GEMV) communication patterns.
3. Exploitation of underutilized routing resources (diagonal links, spare cores, extra channels) through cross-topology remapping, turning redundancy overhead into a performance advantage.
4. Comprehensive evaluation across scales (64×64 to 512×512), fault rates (1%–15%), and workloads (GEMM, GEMV), demonstrating [X%] utilization improvement over discard-based approaches with [Y%] of healthy-mesh performance.

**Results teaser:** Key quantitative highlights (fill in after experiments finalize).

---

## 2. Background & Motivation (~1.5 pages)

### 2.1 From Larger Chips to Defect Tolerance

**Larger chip area directly improves performance.** Integrating more transistors on a single die increases on-chip compute density, memory bandwidth, and cache capacity — but the most critical benefit is eliminating off-chip communication. Data movement across chip boundaries costs 10–100× the energy and latency of on-chip transfers \cite{dally2020domain}, and multi-chip designs face bandwidth cliffs at every packaging level (die → package → board → rack) \cite{arunkumar2017mcm}. This motivates wafer-scale integration: the Cerebras WSE places ~900K cores with 40 GB of distributed SRAM on a single 46,225 mm² wafer, delivering 220 Pb/s on-wafer fabric bandwidth — orders of magnitude beyond what multi-chip packages achieve \cite{lie2023cerebras}.

**However, defects are inevitable — and their impact grows exponentially with area.** Manufacturing defects (random contamination, systematic process variations) occur at a stable density per unit area. Under the industry-standard negative binomial yield model \cite{stapper1983}, yield drops as $Y_R = (1 + D_0 A / \alpha)^{-\alpha}$ — at wafer scale ($A$ = 46,225 mm²), the probability of a defect-free chip is essentially zero. Additionally, intrinsic wear-out mechanisms (electromigration, oxide breakdown) cause further failures over time. Defect tolerance is not optional at this scale; it is a design requirement.

> **[FIGURE PLACEHOLDER — §2.1 Figure: Defects and Mesh Fragmentation]**
> Left: Bathtub curve — extrinsic (manufacturing) → useful life → intrinsic (wear-out), annotating static remapping vs. future online remapping.
> Right: Utilization plot — x-axis: mesh size $W$, y-axis: max defect-free sub-mesh utilization $s^{*2}/W^2$, curves for defect rates 1%, 2%, 4%, 6%, 8%, 10%. Shows catastrophic utilization collapse at wafer scale. (Formal derivation of $s^* \approx \sqrt{2 \ln W / p}$ in Appendix.)

**GPUs and CPUs overcome defects through yield binning.** NVIDIA's GA102 die has 84 SMs but ships the RTX 3090 with 82 and RTX 3080 with 68 — chips with more defective SMs are sold as lower-tier SKUs (Stock Keeping Units) \cite{nvidia2020ga102}. AMD similarly bins Zen 3 CCDs from 8 to 6 cores \cite{gamersnexus2013binning}. This works because GPU SMs are independently connected to the memory system through a GPC–memory partition interconnect \cite{nvidia2020ga102} — disabling one SM does not affect routing or communication for remaining SMs.

**Wafer-scale chips require a fundamentally different approach.** At wafer scale, two architectural choices distinguish the problem:

1. **Small cores to limit defect blast radius.** Rather than a few large cores, wafer-scale designs use hundreds of thousands of small, simple cores. Each core occupies a tiny area, so a single defect disables only one core out of ~900K — minimizing the fraction of compute lost per defect \cite{lie2023cerebras}.
2. **2D mesh as the scalable interconnect.** GPU-style interconnects (multi-stage networks connecting SMs to memory partitions) scale poorly beyond hundreds of endpoints — wire count and switch complexity grow super-linearly. 2D mesh scales with $O(N)$ links and constant router radix, and maps directly to the planar silicon substrate (nearest-neighbor wiring only) \cite{lie2019wafer}. This manufacturing friendliness is fundamental: alternative topologies such as Clos-based switch fabrics can improve communication flexibility \cite{rashidi2025fred}, but they require non-local, non-planar wiring and additional switch area — at odds with the lithographic constraints of wafer-scale integration. This is why all large-scale monolithic architectures (Cerebras WSE) adopt 2D mesh despite its communication limitations.

**But 2D mesh makes defect tolerance fundamentally harder.** In a GPU, each SM is a leaf node — it sends and receives its own traffic but never forwards packets for other SMs. In a 2D mesh, every core also serves as a router for its neighbors. An interior defect therefore creates a routing hole — messages cannot traverse through it, breaking dimension-order routing for all traffic that would cross that point. Even a few defects can drastically limit the maximum contiguous defect-free mesh region. As shown in the figure above, at 1% defect rate on a 750×750 mesh, the largest guaranteed defect-free square is only ~36×36 nodes — **0.23% utilization** (see Appendix for formal proof).

**Cerebras's solution: redundant links + hardware remap.** Rather than discarding defective regions, the Cerebras WSE provisions spare cores and redundant fabric links. A proprietary algorithm routes around defects to expose a regular 2D mesh to software \cite{cerebras2025sigops, luczynski2024reduce}. This achieves high utilization (>93% of cores active), but the algorithm is undisclosed and cannot be reproduced or extended. Furthermore, it only restores regularity — it does not optimize for specific workloads or exploit underutilized routing resources (e.g., diagonal links present in the physical fabric).

### 2.2 AI Inference on Wafer-Scale Mesh Architectures

Having established the physical substrate and its defect challenges, we now examine the AI inference workloads that run on it — and why their structure makes remapping quality critical.

#### 2.2.1 Disaggregated AI Inference: Prefill and Decode

**Prefill vs. Decode phases.** LLM inference consists of two distinct phases with fundamentally different computational characteristics:

- **Prefill phase:** Processes the entire input prompt in parallel. The dominant operation is **GEMM** (matrix–matrix multiplication) — projecting all input tokens through the model's weight matrices simultaneously. This phase is **compute-bound** with high arithmetic intensity.

- **Decode phase:** Generates output tokens one at a time, autoregressively. Each step performs a **GEMV** (matrix–vector multiplication) — the KV-cache matrix is large but the "query" is a single token vector. This phase is **memory-bandwidth-bound** with low arithmetic intensity.

Because prefill and decode have opposite resource requirements (compute-bound vs. memory-bound), running them on the same hardware wastes resources. **Disaggregated inference** separates these phases onto different hardware partitions, each sized and optimized for its workload \cite{zhong2024distserve, patel2024splitwise}.

> **[FIGURE PLACEHOLDER — §2.2 Figure: Prefill vs. Decode Inference Flow]**
> Left: Prefill phase — full input sequence processed in parallel; dominated by GEMM; compute-bound.
> Right: Decode phase — tokens generated autoregressively; dominated by GEMV; memory-bandwidth-bound.
> Bottom: Show how weights are spread across a regular 2D mesh, with communication arrows for each phase.

**Running inference on wafer-scale 2D mesh.** To accelerate these workloads, wafer-scale systems spread each layer's weights and activations across a regular 2D mesh. WaferLLM \cite{he2025waferllm} 2D-tiles each layer's weight matrix across the full mesh (both matrix dimensions mapped to the two mesh axes), with all cores collaborating on one layer via cyclic-shift GEMM (nearest-neighbor systolic data flow) or broadcast-reduce GEMV. Cerebras also supports other execution modes: **Weight Streaming** (weights stored off-chip in MemoryX, streamed layer-by-layer) for models exceeding on-chip capacity, and **Layer Pipelined** (each layer mapped to a rectangular submesh) for smaller models \cite{lie2023cerebras}. Our work targets the on-chip execution model, where weights reside in distributed SRAM and the mesh topology directly governs communication cost.

#### 2.2.2 More Cores ≠ Better Performance on Wafer-Scale Mesh

Wafer-scale systems like the Cerebras WSE offer hundreds of thousands of cores connected via a 2D mesh — an unprecedented amount of parallelism. A natural expectation is that allocating more cores to an inference workload always improves performance. **This is not the case.**

The two inference phases scale very differently with mesh size \cite{he2025waferllm}:

- **GEMV (decode) can degrade when cores are too many.** Because decode is memory-bandwidth-bound, the per-core computation is already small. As the mesh grows, each core's local work shrinks further while the allreduce communication tree deepens — more hops, more latency. Beyond an optimal mesh size, communication dominates >90% of total latency, and adding more cores actually *increases* end-to-end decode time.

- **GEMM (prefill) still benefits from more cores.** Because prefill is compute-bound, the heavy matrix–matrix computation dominates over communication. WaferLLM's cyclic-shift algorithm bounds the critical communication path per shift step to a constant 2 hops regardless of mesh size, so compute time reduction outweighs the communication overhead — achieving >70% computational efficiency even at 720×720 cores. However, for small matrices, communication overhead can still dominate.

WaferLLM confirms this asymmetry in practice: for LLaMA3-8B, it uses 660×660 cores for prefill but only 360×360 for decode — nearly 3.4× fewer cores for the memory-bound phase. This has two implications:

1. **Optimal mesh size is workload-dependent.** For a given model and sequence length, there exists an optimal $M \times M$ partition — smaller than the full wafer — beyond which adding cores hurts. The remapper must carve out *right-sized* virtual meshes, not just the largest possible one.
2. **Remapping quality matters, not just utilization.** A naive remapper that maximizes core count but ignores communication patterns may land on the wrong side of the trade-off. A workload-aware remapper can target the right operating point by minimizing hop stretch for critical communication edges (systolic shifts for GEMM, broadcast/reduce trees for GEMV). On a defective mesh, this is even more critical — remapped virtual neighbors may be multiple physical hops apart, further worsening communication overhead. We formalize this with an analytical model in §6.1.

**Why not simply use small defect-free meshes?** For small models and short contexts, a modest mesh may suffice — but for large batch sizes, long context lengths, and large models, the aggregate SRAM across many cores is needed to store KV-cache and model weights (WaferLLM cannot fit CodeLLaMA-34B or QWen2-72B in a single WSE-2's memory \cite{he2025waferllm}). Even the memory-bound decode phase still requires a substantial mesh for storage capacity. Moreover, intrinsic wear-out (§2.1) means defect counts grow over time — a mesh that meets a workload's size requirement today may not tomorrow. On a defective wafer, right-sized partitions may not exist as contiguous defect-free regions, and this problem only worsens with device aging — making workload-aware *remapping*, not just partitioning, essential.

### 2.3 Opportunity: Workload-Aware Remapping

§2.1 establishes that defects are inevitable at wafer scale and that they seriously degrade mesh performance — even a small defect rate fragments the physical substrate, leaving only a tiny fraction usable as contiguous regular mesh. §2.2 shows that AI inference workloads have phase-specific communication requirements (GEMM for prefill, GEMV for decode) and that performance is sensitive to mesh sizing and layout quality. Together, these observations motivate a remapping approach that operates at three levels:

1. **Remap over defective mesh to expose regular virtual topology, with deadlock-free routing.** Rather than discarding defective regions or relying on proprietary hardware remapping, we map a virtual regular mesh onto all healthy nodes of the defective physical substrate — recovering the >99% of cores that discard-based approaches abandon (§2.1: at 1% defect rate, discard yields only 0.23% utilization). Remapping onto irregular physical paths introduces the risk of cyclic channel dependencies (deadlock); our framework guarantees deadlock freedom via a submesh-hierarchy routing scheme, making the remapped topology safe for production use.

2. **Optimize remapping for workload communication patterns.** A topology-only remapping (like Cerebras's regularity restoration) ignores the workload running on the mesh. As WaferLLM demonstrates (§2.2.2), performance is highly sensitive to mesh sizing and communication layout — decode throughput can *decrease* with more cores. Since prefill and decode have fundamentally different communication patterns — systolic nearest-neighbor shifts (GEMM) vs. broadcast/reduce trees (GEMV) — the remapper should minimize hop stretch along the edges that matter most for each phase. This enables right-sized virtual partitions optimized for each inference stage.

3. **Exploit redundant resources to further mitigate remapping overhead.** Remapping onto a defective substrate inevitably introduces some performance overhead (increased hop count, link contention). Current industrial solutions hide spare cores, extra links (e.g., diagonal connections), and additional virtual channels behind a regular facade — the Cerebras WSE, for instance, has 24 virtual channels and diagonal fabric links that are concealed from software (§2.1). Instead of concealing these resources, our remapper exposes and utilizes them — diagonal links as routing shortcuts to reduce hop count, spare cores as additional compute, and extra channels for routing flexibility — actively compensating for the remapping overhead.

---

> **Archived subsections** (moved from §2 during restructuring — retained for reference, may be incorporated into §3 or §7):

<details>
<summary>Archived: Parallelism Strategy Taxonomy (removed from §2.2.1 — general background, not wafer-specific)</summary>

To serve large language models (LLMs) at scale, a model is partitioned across accelerator cores using parallelism strategies — primarily tensor/model parallelism (MP), pipeline parallelism (PP), and data parallelism (DP), with sequence parallelism (SP) and expert parallelism (EP) for specific scenarios \cite{shoeybi2019megatron, narayanan2021efficient, lepikhin2021gshard}.

</details>

<details>
<summary>Archived: Detailed Yield Models and Defect Type Details (condensed from §2.1.1 — for ASPLOS appendix)</summary>

**Full yield model progression (random defects):**
- **Poisson model** \cite{murphy1964}: $Y = e^{-D_0 A}$ — assumes defects are uniformly distributed across the wafer. Simple but systematically underestimates yield because real defects tend to cluster spatially.
- **Murphy's model** \cite{murphy1964}: $Y = \left(\frac{1 - e^{-D_0 A}}{D_0 A}\right)^2$ — introduced a probability distribution over defect density to account for wafer-to-wafer variation, improving accuracy over pure Poisson.
- **Seeds' model** \cite{seeds1967}: $Y = e^{-\sqrt{D_0 A}}$ — an empirically-motivated model that better fits observed yields at moderate defect densities.
- **Negative binomial model** \cite{stapper1983}: $Y_R = (1 + D_0 A / \alpha)^{-\alpha}$ — incorporates defect clustering via the cluster parameter $\alpha$ (smaller $\alpha$ = more clustering). Derived by Stapper et al. using a compound Poisson distribution with gamma-distributed defect density. This became the industry-standard model; Cunningham (1990) \cite{cunningham1990} provides a comprehensive evaluation of these models.

**Detailed systematic defect patterns:** Edge-Ring (thermal non-uniformity at wafer periphery), Center (CMP pressure imbalance), Scratch (mechanical handling), Local (localized process excursion), Donut (edge-to-center process gradient) \cite{xu2022wafermap}. Each maps to a specific equipment or process root cause. Lithographic marginalities produce metal islands causing shorts/opens; contact spacing variations create middle-of-line failures; edge-band effects can cause >5% die loss at the wafer periphery.

**Detailed intrinsic defect mechanisms:**
- **Electromigration (EM):** momentum transfer from current-carrying electrons gradually displaces metal atoms in interconnects, forming voids (open circuits) or hillocks (shorts). Accelerated by high current density and temperature; becomes worse at smaller wire cross-sections.
- **Gate oxide breakdown (TDDB — Time-Dependent Dielectric Breakdown):** progressive charge trapping in the gate dielectric creates a conductive path through the oxide, eventually causing permanent gate-to-channel shorts. Thinner oxides at advanced nodes accelerate this mechanism.
- **Hot carrier injection (HCI)**, **bias temperature instability (BTI)**, and **stress migration** further contribute to gradual parametric drift and eventual hard failure.

**Implications for our work (removed from §2.1.1 to avoid premature design references):**
- **Extrinsic defects** (both random and systematic) are known at manufacturing/boot time — the remapper can compute a static mapping once. Random defects produce the spatially uniform i.i.d. fault model used in most prior topology reconfiguration work (including Zhang et al.) and in our baseline experiments. Systematic defects produce spatially correlated fault clusters — entire rows, rings, or zones of adjacent cores may fail together, creating larger "holes" in the physical mesh. Our hierarchical RCB partitioning naturally adapts to both: it partitions around defect-dense regions regardless of whether the pattern is random or clustered.
- **Intrinsic wear-out** creates faults that emerge during operation — cores, routers, or links that were healthy at boot time may fail later. This motivates future work on online/incremental remapping (§8.2), but the offline remapping framework we present is the necessary foundation.

</details>

<details>
<summary>Archived: Summary of Industrial Defect Tolerance Mechanisms (formerly §2.1.3)</summary>

| Approach | Example | Mechanism |
|----------|---------|-----------|
| Yield binning | NVIDIA GA102, AMD Zen 3 | Over-provision compute units, fuse off defective ones, sell as different SKUs \cite{nvidia2020ga102, gamersnexus2013binning} |
| Edge discard | Tilera TILE-Gx72 | Fuse off edge cores in mesh to produce lower SKUs; discard die on interior defect \cite{tilera2013tilegx} |
| Spare cores + remap | Cerebras WSE, Tesla Dojo D1 | Provision ~1.5–7% spare cores; remap around defects to expose regular mesh \cite{luczynski2024reduce, cerebras2025sigops, talpes2023dojo} |

</details>

<details>
<summary>Archived: Defect Tolerance Details (removed during §2.1 rewrite — for ASPLOS appendix or detailed version)</summary>

**Bathtub Curve defect taxonomy (full version):**

Defects in semiconductor manufacturing follow the Bathtub Curve — high infant mortality, a stable useful-life period, then increasing wear-out failures:

**Extrinsic defects (manufacturing-induced)** are present from fabrication and comprise two sub-types:

- **Random defects** arise from stochastic contamination (particles, micro-scratches, cleanroom noise). They are spatially uncorrelated with a stable mean density per unit area \cite{xu2022wafermap}. The industry-standard yield model is the **negative binomial** \cite{stapper1983}: $Y_R = (1 + D_0 A / \alpha)^{-\alpha}$, where $D_0$ is defect density, $A$ is die area, and $\alpha$ captures defect clustering (earlier models by Murphy \cite{murphy1964} and Seeds \cite{seeds1967} are special cases; see Cunningham \cite{cunningham1990} for a comprehensive comparison). As area $A$ grows, $Y_R \to 0$ — at wafer scale, zero-defect fabrication is essentially impossible.

- **Systematic defects** are spatially correlated failures from process variations (lithographic limits, CMP non-uniformity, etch loading, thermal gradients). They produce recognizable wafer map signatures — Edge-Ring, Center, Scratch, Local, Donut — each diagnostic of a specific process root cause \cite{xu2022wafermap}. At advanced nodes (sub-7nm), systematic defects surpass random defects as the primary yield concern \cite{semiengineering2024systematic}.

**Intrinsic defects (wear-out)** emerge over time as devices degrade: electromigration (EM), gate oxide breakdown (TDDB), hot carrier injection (HCI), and bias temperature instability (BTI). These cause cores and links that were healthy at boot time to fail during operation.

At wafer scale (Cerebras WSE: 46,225 mm² die area), all defect types are present — defect tolerance is not optional, it is a design requirement. Extrinsic defects are known at manufacturing/boot time and can be addressed by static remapping; intrinsic wear-out motivates future work on online remapping (§8.2).

**Yield decomposition:**

The overall die yield $Y = Y_M \cdot Y_S \cdot Y_R$ — each factor compounds, and all decrease with die area $A$.

**Tilera edge-discard example:**

Tilera's TILE-Gx72 (8×9 on-chip mesh, 5 physical networks, XY routing) performs yield binning by fusing off **edge** cores to produce lower SKUs (72→36→16→9 cores). However, an interior router defect forces the **entire die to be discarded** — there is no mechanism to route around an interior hole in the mesh \cite{tilera2013tilegx}.

**Maximum defect-free sub-mesh proof ($s^*$):**

For a $W \times W$ physical mesh with i.i.d. node defect probability $p$, the largest defect-free $s \times s$ sub-mesh has expected side length (see `reference/max_spacing_derivations.md` for full derivation):

$$s^* \approx \sqrt{\frac{2 \ln W}{p}}$$

This follows from a threshold argument: an $s \times s$ sub-mesh survives with probability $(1-p)^{s^2}$, and there are $(W-s+1)^2$ possible placements. Setting the expected count of surviving sub-meshes to 1 and solving gives the formula above.

**Concrete impact:** For a Cerebras-class mesh ($W = 750$, $p = 0.01$):

$$s^* \approx \sqrt{\frac{2 \ln 750}{0.01}} = \sqrt{\frac{2 \times 6.62}{0.01}} \approx 36$$

Out of a 750×750 = 562,500-node mesh, the largest guaranteed defect-free square is only ~36×36 = 1,296 nodes — **0.23% utilization**. The discard approach wastes >99.7% of healthy silicon.

| $W$ | $p$ | $s^*$ (side) | $s^{*2}/W^2$ (utilization) |
|-----|-----|-------------|---------------------------|
| 100 | 1% | 30 | 9.0% |
| 500 | 1% | 35 | 0.49% |
| 750 | 1% | 36 | 0.23% |
| 750 | 5% | 16 | 0.046% |

The critical scaling: $s^*$ grows only as $\sqrt{\ln W}$ — essentially flat — while the total mesh area grows as $W^2$. Increasing the physical mesh barely helps the discard approach.

**Tesla Dojo D1 reference:**

Tesla Dojo D1 similarly reserves 6 of 360 cores (1.7%) as spares \cite{talpes2023dojo}.

</details>

<details>
<summary>Archived: The Compute–Communication Trade-Off Details (formerly §2.2.3)</summary>

The WaferLLM observation reflects a fundamental trade-off in mesh-based parallel computing: adding more cores to a fixed-size workload reduces per-core computation but increases communication overhead. Each core holds a smaller data partition, so it finishes computing faster — but it must exchange data with neighbors over more hops, and the mesh becomes more congested as paths from different cores overlap on shared physical links.

On a **healthy mesh**, this creates a sweet spot: an optimal mesh size $M^*$ that minimizes total execution time for a given workload. Going beyond $M^*$ hurts rather than helps.

On a **defective mesh after remapping**, the trade-off worsens. Virtual neighbors that were one hop apart on the ideal mesh may be multiple physical hops apart after remapping around defects. This extra hop stretch increases communication latency and link contention, pushing the sweet spot toward fewer cores. The *quality* of the remapping — how well it preserves locality between communicating virtual neighbors — directly determines how much performance is lost relative to the healthy baseline.

**This is why remapping quality matters, not just utilization.** A naive remapper that maximizes core count but ignores communication patterns may land on the wrong side of the trade-off — using more cores but performing worse. A workload-aware remapper can target the right operating point by minimizing hop stretch for the workload's critical communication edges (systolic shifts for GEMM, broadcast/reduce trees for GEMV).

</details>

<details>
<summary>Archived: Limitations of Current Industrial Approaches (formerly §2.1.3)</summary>

| Approach | Mechanism | Limitation |
|----------|-----------|------------|
| Yield binning (NVIDIA, AMD, Intel) | Over-provision, fuse off defective SMs/CUs/cores, sell as lower SKU | Only works for independent/crossbar-connected units; not applicable to mesh-connected architectures |
| Edge discard (Tilera TILE-Gx) | Fuse off edge cores; discard die on interior defect | Cannot tolerate interior faults in mesh topology |
| Spare cores + proprietary remap (Cerebras WSE) | ~1.5% spare cores; undisclosed algorithm routes around defects \cite{luczynski2024reduce, cerebras2025sigops} | Algorithm not published; does not optimize for workload or exploit diagonal links |

**The gap:** No existing industrial solution provides an open, workload-aware remapping algorithm for mesh-connected architectures. Yield binning and edge discard cannot handle interior mesh defects. Cerebras's approach achieves high utilization but is proprietary and topology-unaware — it restores a regular mesh without optimizing for specific workloads or exploiting underutilized routing resources (e.g., diagonal links).

</details>

<details>
<summary>Archived: Regular Topology Is a Software Requirement (formerly §2.2)</summary>

- High-performance kernels (systolic GEMM, broadcast+reduce GEMV) are designed for regular 2D mesh:
  - Uniform neighbor count enables systolic dataflow.
  - Dimension-order routing gives deterministic latency.
  - Programming models assume a clean coordinate space.

</details>

<details>
<summary>Archived: Symmetric vs. Asymmetric Topologies (formerly §2.4)</summary>

- **Symmetric topologies (e.g., Clos):** fault tolerance is nearly solved.
  - All middle-stage switches are functionally interchangeable — losing one merely reduces path diversity.
  - Acyclic structure means rerouting never causes deadlock; at worst, congestion.
  - Recovery is polynomial-time edge-coloring.
- **Why Clos is not always an option:**
  - Clos requires multi-stage switching fabric with non-local, non-planar interconnects. On a 2D silicon die or interposer, this means long cross-chip wires, additional metal layers, and large crossbar switches — fundamentally at odds with the planar, nearest-neighbor wiring that lithographic manufacturing naturally provides.
  - 2D mesh maps directly to the physical substrate: each node connects only to its immediate neighbors, making it area-efficient and manufacturing-friendly at any scale.
  - This is why all large-scale monolithic chips (Cerebras WSE) and chiplet interposers use 2D mesh or torus, not Clos.
- **Asymmetric topologies (e.g., 2D mesh):** every node is topologically unique → defect tolerance is fundamentally harder.
  - Rerouting around faults can introduce cyclic channel dependencies → deadlock.
  - The remapping problem (embedding a virtual regular mesh into a faulty physical mesh) is NP-hard (reduces from subgraph isomorphism).
  - No prior work addresses remapping at large scale (>128 nodes) with workload awareness and deadlock-free routing.

</details>

---

## 3. Challenges (~0.75 page)

> **Structural note:** Challenges are ordered by dependency: correctness (can we do this safely?) → quality (can we do this well?) → practicality (can we do this at scale?). Each maps to a design component in §4.

### 3.1 Deadlock-Free Routing on Irregular Topology → addressed by §4.4–4.5

> **[FIGURE PLACEHOLDER — §3.1 Figure: Routing Hazards After Remapping]**
> Left: A small virtual mesh (e.g., 3×3) with a single virtual hop A→B shown as one link. Middle: After remapping onto a defective physical mesh, the same virtual hop A→B becomes a multi-hop physical detour around a faulty node. A virtual communication spanning multiple hops (A→B→C) is the concatenation of two physical detours. Right: The concatenated path revisits a physical node — show (a) cyclic channel dependency between two intersecting paths (deadlock), and (b) a path cycle where a packet re-enters a node and fans out again (broadcast storm / infinite duplication).

Remapping a virtual mesh onto a defective physical mesh fundamentally changes the routing structure. On the original (defect-free) mesh, each virtual link is a single physical hop, and dimension-order routing (XY) is trivially deadlock-free. After remapping, a single virtual hop between two virtual neighbors may map to a **multi-hop physical path** that detours around faulty nodes. A virtual communication that traverses several virtual hops now becomes the **concatenation** of these multi-hop physical segments. Crucially, the individual segments may each be valid, but their concatenation can revisit physical nodes and physical channels in arbitrary order — destroying the monotonic channel usage that made XY routing safe.

This concatenation mechanism is the root cause of three correctness hazards:

- **Deadlock (cyclic channel dependency):** When multiple virtual communications are mapped to concatenated multi-hop physical paths, their physical segments may share and contend for the same physical channels in opposing directions. These intersections create cyclic dependencies in the channel dependency graph (CDG) — messages block forever waiting for each other. The Dally-Seitz theorem \cite{dally1987deadlock} establishes that deadlock freedom requires an acyclic CDG, but the concatenation of independently-routed segments provides no such guarantee.
- **Infinite duplication (path cycles from concatenation):** Because each virtual hop maps to a different physical detour, the concatenated end-to-end path can visit the same physical node twice. At that node, the stateless routing table cannot distinguish first visit from second — every arrival fans out to all encoded output ports. The cycle produces copies that return and fan out again, causing exponential packet duplication that never terminates (a "broadcast storm").
- **Multicast amplification:** For multicast operations (e.g., GEMV broadcast/reduce), branch intersections at a router duplicate flits from converging branches, each of which may themselves contain concatenation-induced cycles — compounding the duplication problem exponentially.

Existing approaches either avoid the problem entirely (SpiNNaker: migrate tasks instead of rerouting; Cerebras: proprietary solution) or provide only partial guarantees (up*/down* routing limits path diversity). **Need:** a routing scheme that (a) finds valid physical paths for all virtual communications, (b) guarantees acyclic CDG (deadlock freedom), and (c) guarantees cycle-free paths (no node visited twice) to prevent infinite duplication.

### 3.2 Workload-Aware Mapping Quality → addressed by §4.2–4.3

Even with correct routing, the *quality* of the virtual-to-physical mapping determines performance. The mapping problem is a constrained subgraph embedding — formally, finding an injective function $f: V_v \to V_p$ that minimizes a cost function over all virtual edges. This generalizes subgraph isomorphism and is NP-hard \cite{rost2020hardness}.

The challenge is not just computational hardness but *what to optimize*:

- **Topology-only cost is insufficient.** Minimizing total hop count treats all virtual edges equally. But if two virtual nodes never communicate, their physical distance is irrelevant. Conversely, edges on the critical path of a systolic GEMM must be as short as possible.
- **Different workloads need different mappings.** GEMM (systolic) has strict nearest-neighbor row/column shifts where hop uniformity is critical for synchronization. GEMV (broadcast+reduce) has long-range collective operations where tree depth and fan-in balance matter more than individual hop counts. In Mixture-of-Experts (MoE) layers, only a subset of experts activate per token — expert placement on the mesh creates input-dependent, non-uniform traffic patterns where poorly placed experts become congestion hotspots.

**Need:** a workload-aware cost function that weights mapping quality by actual communication volume and pattern, separately tunable for prefill (GEMM) and decode (GEMV). We show in §6 that a topology-only mapping can lose significant performance compared to a workload-aware one.

### 3.3 Scalability to Wafer-Scale Meshes → addressed by §4.2 Hierarchical Spatial Search

Given that the mapping problem is NP-hard (§3.2), exact algorithms are infeasible at wafer scale:

- **Exact subgraph matching** (Ullmann 1976, VF2 2004, VF3 2017) has exponential worst-case complexity, making it intractable for meshes with hundreds of thousands of nodes. Worse, as defects accumulate, an exact isomorphic match may not even exist — the defective physical mesh may lack any subgraph structurally identical to the desired virtual mesh, rendering exact methods infeasible regardless of compute budget.
- **Metaheuristics** — simulated annealing (Zhang et al. \cite{zhang2009topology}) and memetic algorithms (Qian et al. \cite{qian2024memetic}) — improve over exact methods but remain too slow at wafer scale due to iterative global search. Zhang et al. report results only up to 128 nodes.
- **The search space is vast.** The Cerebras WSE-3 has 900K cores \cite{lie2023cerebras}. Even after removing defective nodes, the number of candidate placements for a virtual mesh of tens of thousands of nodes onto a physical substrate of hundreds of thousands of healthy nodes is astronomically large.

**Need:** a hierarchical heuristic that decomposes the problem spatially, reducing per-node search from $O(M)$ (exhaustive over physical mesh) to $O(\log M)$ (KdTree-indexed), enabling near-linear scaling to wafer-scale meshes.

---

## 4. Design: Model-Defined Remapper (~2.5 pages)

### 4.1 Overview

> **[FIGURE PLACEHOLDER — §4.1 Figure: Framework Overview]**
> End-to-end pipeline diagram.
> **Inputs** (left): (1) AI model compute graph (hardware-agnostic), (2) Remapper configuration, (3) Virtual NoC specification, (4) Hardware info (core capabilities, link bandwidth, etc.), (5) Defect map (faulty nodes/links).
> **Pipeline** (center): **Compile (§4.2)** → **Init Anchor (§4.3)** → **Iterative Frontier Expansion (§4.4)** with interleaved routing and cost evaluation → **Output**.
> **Output** (right): Node mapping $f: V \to P$ + static deterministic routing tables.
> Show the iterative loop in §4.4: expand frontier → build routing paths for covered dataflow → evaluate node cost + routing cost across multiple trials → pick best trial → repeat.

**Inputs.** The remapper takes five inputs: (1) an AI model compute graph describing the workload's dataflow in hardware-agnostic form; (2) a remapper configuration (candidate pool size, number of trials, etc.); (3) a virtual NoC specification (the target regular mesh topology); (4) hardware information (core capabilities, link bandwidth, memory per core); and (5) a defect map identifying faulty nodes and links on the physical substrate.

**Output.** The remapper produces a node mapping $f: V \to P$ from virtual mesh nodes to healthy physical nodes, together with static, deterministic routing tables that specify the physical path for every virtual communication edge. These routing tables are guaranteed deadlock-free (§4.5).

**Pipeline.** The remapping proceeds in four stages:

1. **Compile (§4.2):** Translate the hardware-agnostic compute graph into a hardware-aware compute graph with explicit communication edges (GEMM systolic shifts, GEMV broadcast/reduce, etc.) and traffic volume annotations.
2. **Init Anchor (§4.3):** Select an anchor node on the physical mesh and map the corresponding virtual node to it, initializing both virtual and physical frontier node sets.
3. **Iterative Frontier Expansion (§4.4):** The core mapping loop. At each iteration:
   - Expand the mapping by matching unmapped virtual frontier neighbors to physical frontier neighbors, evaluating multiple candidate trials in parallel.
   - For each trial, build routing paths for the dataflow edges covered so far, then compute a combined node cost + routing cost.
   - Select the trial with the lowest total cost; advance the frontier.
4. **Output:** Emit the final node mapping and routing tables. Routing is verified deadlock-free via submesh-hierarchy constraints (§4.5).

**Assumptions:**
- The physical NoC supports ≥2 virtual channels (VCs) for deadlock-free routing (§4.5). (Additional assumptions to be added.)

### 4.2 Compute Graph Compilation

The remapper's first stage translates a hardware-agnostic AI model compute graph into a hardware-aware communication graph. The input graph describes the model's dataflow (e.g., layers, activations, weight accesses) without reference to specific hardware. The compiler:

- Decomposes each layer into the concrete communication operations for the target mesh: **systolic shifts** (nearest-neighbor row/column data flow for GEMM), **broadcast/reduce trees** (for GEMV), and **point-to-point transfers** (for pipeline stage boundaries).
- Annotates each communication edge with **traffic volume** (bytes per inference step) derived from the model's tensor dimensions and parallelism configuration.
- Produces a hardware-aware compute graph where each node corresponds to a virtual mesh tile and each edge carries a communication type and volume — this graph drives the workload-aware cost function in §4.4.

**Decomposition into primitive tasks.** Crucially, the compilation step decomposes named high-level operations (e.g., GEMM, GEMV, attention) into primitive per-core **transmission** and **computation** tasks, organized as a per-core dependency graph. Each task is one of three types: *send* (inject a message of a given size to a destination core), *receive* (wait for a message from a source core), or *process* (execute a computation for a specified duration). This decomposition decouples the remapper from operator-level semantics — a "GEMM" or "GEMV" is not a named black box but a specific dataflow pattern of sends, receives, and local compute across a group of cores. The remapper and cost function reason only about these primitives, making the framework extensible to new operators without modifying the mapping algorithm.

This decomposition philosophy is analogous to how Yoo et al. \cite{yoo2025standardized} extend the Chakra Execution Trace format to represent collective algorithms (All-Reduce, All-Gather, etc.) as graphs of primitive COMM\_SEND, COMM\_RECV, and COMP nodes — decoupling the algorithm implementation from the collective's name. Our work applies the same principle at a different level: rather than decomposing *communication collectives* across distributed NPUs, we decompose *compute operators* into per-core task graphs on a spatial mesh architecture. This finer granularity enables the remapper to co-optimize placement and routing with respect to the actual dataflow, and to model compute-communication overlap at the task level (e.g., a core can begin local computation while still receiving data from neighbors).

### 4.3 Anchor Initialization

The mapping begins by anchoring a single virtual node to a physical node. The anchor determines the global position and orientation of the virtual mesh on the physical substrate.

- Select an anchor physical node based on spatial centrality within the healthy region (maximizing the available expansion space in all directions).
- Map the corresponding virtual node (e.g., the center of the virtual mesh) to this anchor.
- Initialize the **frontier**: the set of virtual nodes adjacent to already-mapped nodes, paired with the set of candidate physical nodes adjacent to already-mapped physical nodes.

### 4.4 Iterative Frontier Expansion with Interleaved Routing

> **[ALGORITHM PLACEHOLDER — Algorithm 1: Frontier Expansion with Interleaved Routing]**
> ```
> Input: Hardware-aware compute graph G, Physical mesh P (defects removed),
>        Virtual NoC V, Anchor mapping (v_0 → p_0)
> Output: Mapping f: V → P, Routing tables R
>
> frontier_v ← neighbors of v_0 in V
> frontier_p ← neighbors of p_0 in P (healthy only)
> mapped ← {v_0 → p_0}
>
> while frontier_v is not empty:
>   // Generate multiple candidate trials
>   for each trial t in 1..T:
>     Pick next unmapped virtual node v from frontier_v
>     Select candidate physical node p_t from frontier_p neighbors
>     Tentatively map v → p_t
>
>     // Interleaved routing: build paths for newly covered edges
>     For each dataflow edge (v, v') where both v and v' are now mapped:
>       Compute physical routing path from f(v) to f(v')
>       Ensure path avoids faulty nodes and previously allocated channels
>
>     // Cost evaluation
>     node_cost_t ← evaluate geometric + neighbor displacement cost
>     routing_cost_t ← evaluate hop stretch × traffic volume + link congestion
>     total_cost_t ← node_cost_t + routing_cost_t
>
>   // Select best trial
>   t* ← argmin(total_cost_t)
>   Commit mapping and routing paths for trial t*
>   Update frontier_v and frontier_p
>
> return mapped, routing_tables
> ```

This is the core of the remapper. Key design decisions:

- **Frontier-based expansion** ensures spatial locality — each new mapping is adjacent to already-mapped nodes, preserving the mesh structure and avoiding fragmented placements.
- **Interleaved routing** evaluates routing cost *during* mapping, not after. This is critical: a node placement that looks good by coordinate distance may create long or congested routing paths. By building routes incrementally, the cost function captures the actual physical communication cost at each step.
- **Multiple trials** at each expansion step explore different candidate physical nodes in parallel, avoiding greedy local minima. The trial with the lowest combined node + routing cost is committed.
- **Routing paths are static and deterministic** — computed once during mapping and fixed for deployment. This enables offline verification of deadlock freedom (§4.5) and eliminates runtime routing overhead.

### 4.5 Cost Function (used within §4.4)

The cost function scores each trial along two dimensions, evaluated together at each frontier expansion step:

**Node cost:**
- **Coordinate displacement:** geometric distance between the virtual node's expected position and the candidate physical position.
- **Neighbor consistency:** how well the candidate preserves adjacency — mapped virtual neighbors should be physically close.

**Routing cost:**
- **Hop stretch × traffic volume:** for each routed dataflow edge, the physical hop count weighted by the edge's communication volume. High-traffic edges (systolic shifts in GEMM, broadcast trunks in GEMV) are heavily penalized if mapped to long paths.
- **Link congestion:** penalizes mappings that overload physical links shared by multiple routes.

The cost function is separately tunable for prefill (GEMM-dominated) and decode (GEMV-dominated) workloads, enabling the remapper to produce phase-specific mappings.

### 4.6 Deadlock-Free Routing via Submesh Hierarchy

> **[ALGORITHM PLACEHOLDER — Algorithm 2: Submesh-Hierarchy Deadlock Resolution]**
> ```
> Input: Mapped physical mesh, Routing paths from §4.4
> Output: Deadlock-free routing tables with VC assignments
>
> Step 1 — Build submesh hierarchy:
>   Recursively partition mapped physical mesh into hierarchy of submeshes
>
> Step 2 — Assign hierarchical levels:
>   Each physical node belongs to submeshes at multiple levels
>
> Step 3 — Route with ascend-then-descend constraint:
>   For each routing path:
>     Phase 1 (ascend): route on ascending VC, moving to coarser submeshes
>     Phase 2 (descend): route on descending VC, moving to finer submeshes
>     No re-ascent allowed → total order on channel usage → acyclic CDG
>
> Step 4 — Verify:
>   Confirm CDG is acyclic; confirm no path visits any node twice
> ```

- **Problem:** Arbitrary physical paths on an irregular topology can create cycles in the channel dependency graph (CDG), causing deadlock (§3.1).
- **Solution:** Submesh-hierarchy routing with *ascend-then-descend* constraint:
  - Partition the mapped physical mesh into a hierarchy of submeshes.
  - Each routing path first ascends the hierarchy (coarse submeshes) on one VC, then descends (fine submeshes) on another VC.
  - **No re-ascent allowed** → the hierarchical ordering imposes a total order on channel usage → acyclic CDG → deadlock freedom.
- **Broadcast storm prevention:** Deterministic, non-duplicating forwarding — each message follows exactly one path. Combined with the cycle-free path guarantee (no node visited twice), this eliminates infinite duplication.
- Works for both 4-connected (standard mesh) and 8-connected (diagonal mesh) topologies.
- **Hardware requirement: ≥2 virtual channels (VCs).** The ascending and descending phases use separate VCs. This is a conservative assumption — modern wafer-scale architectures provide far more:
  - Cerebras WSE: **24 colors** (true VCs, any color can carry any data) \cite{cerebras2024sdk}
  - Google TPU ICI: **≥2 VCs** for dateline-based deadlock-free torus routing
  - Historically, 2 VCs is the minimum for deadlock-free torus routing (Cray T3D/T3E, IBM Blue Gene/L)
  - Li et al. (ISCA 2024) prove that all practical coherence protocols require ≥2 virtual networks for deadlock freedom \cite{li2024minvn}

> **[NOTE — Adversary case to address in paper:]** Real VC-free mesh products exist (Kalray MPPA-256, Tilera TILE-Gx, Adapteva Epiphany, SpiNNaker). However: single-die products discard the entire die on interior defects; Adapteva's multi-chip mesh never solved the hole-in-mesh problem; SpiNNaker tolerates packet loss (unacceptable for deterministic compute). The only products that handle interior mesh defects losslessly (Cerebras 24 VCs, TPU ≥2 VCs) all use virtual channels. **≥2 VCs is the inherent cost of remapping over waste.** See `reference/Virtual_Channels_in_Modern_Hardware.md` for full details.

---

## 5. Implementation (~0.5 page)

- Implemented in Rust (workspace: Common, Util, IR, NoC, Mapper, Simulator, Experiments).
- Parallel evaluation via rayon; light-weight mesh representation for large scales (flat arrays instead of Rc/RefCell for 512×512+).
- Workload IR: task/work abstractions encoding GEMM (systolic) and GEMV (broadcast+reduce) communication patterns.
- Latency predictor with congestion awareness for cost evaluation.
- Configuration: bandwidth, FLOPS, latencies, fault rates, mapper parameters (candidate pool size, RANSAC iterations, etc.).

---

## 6. Evaluation (~2.5 pages)

> **Evaluation philosophy (learned from Stratum/MICRO '25):** Evaluate at multiple levels — algorithm, architecture, workload, and practicality. Each experiment should answer a specific question. Include overhead analysis to preempt reviewer concerns.

### 6.1 Analytical Performance Model

> Note: The core performance model and U-shape trade-off are now introduced in §2.2.3 as motivation. This section provides the full parameterization and uses it to frame experimental results.

**Transmission time decomposition:**
```
t_transmission = t_routing + t_link_queuing + t_ejection_queuing
```
- `t_routing`: deterministic latency from injection at src to ejection at dst (modelable)
- `t_link_queuing`: waiting for shared links/channels along the path (hard to predict, measured via simulation)
- `t_ejection_queuing`: waiting to eject at dst when multiple messages arrive simultaneously (hard to predict, measured via simulation)

**Routing latency (Hockney model + wormhole routing):**
```
t_routing = α + β·M_msg

α = H·(t_rt + t_ch)          -- head flit traversal: H hops, each through a router and a channel
β = 1 / BW                   -- pipeline drain rate; BW = frequency × flit_size (bytes/sec)
M_msg = message size in bytes -- depends on element count × element size S
```

**GEMM latency model (Cannon-type algorithm):**

For matrix dimension N×N on mesh dimension M×M, element size S bytes (e.g., 2 for FP16, 4 for FP32):
```
t_GEMM = t_comp + t_comm + t_queuing

t_comp = (N/M)³ · M · t_mac              = N³/(M² · FLOPS_per_PE)    [decreases as 1/M²]
t_comm = H·(t_rt + t_ch) + M·(N/M)²·S/BW = H·(t_rt + t_ch) + N²·S/(M·BW)
         ↑ head flit (once)                  ↑ pipeline serialization (M steps)
t_queuing ≈ f(link_sharing, path_intersection)  [measured via simulation]

where:
  N×N      = matrix dimension
  M×M      = mesh dimension (number of PEs = M²)
  S        = element size in bytes (2 for FP16, 4 for FP32, etc.)
  H        = physical hops per virtual neighbor shift (= 1 on healthy mesh, > 1 after remapping)
  t_mac    = time per multiply-accumulate (MAC) operation (= 1/FLOPS_per_PE)
  t_rt     = router traversal latency
  t_ch     = channel traversal latency
  BW       = link bandwidth in bytes/sec (= frequency × flit_size)
```

**Queuing on a healthy mesh:**
All PEs shift data in the same direction simultaneously (A left, B up). Each link carries exactly one message per step → no link contention (t_link_queuing = 0). However, each PE receives submatrices from both its horizontal and vertical neighbors (A shifts left, B shifts up), so if these two arrivals overlap in time, ejection queuing occurs (t_ejection_queuing > 0 even on healthy mesh).

**After remapping, queuing worsens:**
- Virtual 1-hop becomes physical multi-hop (H > 1) → different virtual shifts share physical links → t_link_queuing > 0 (new source of delay)
- Ejection queuing effect is ambiguous: asymmetric physical path lengths may desynchronize arrivals (reducing overlap vs. healthy mesh where both neighbors are 1-hop away and arrive simultaneously), but irregular mappings may also cause unexpected convergence from multiple sources. Net effect depends on the specific mapping — measured via simulation

**U-shape trade-off (key insight for the paper):**

Given fixed N, plot t_GEMM vs M:
- t_comp = N³/M² · t_mac → decreases with M
- t_comm: head flit term grows with H(M), pipeline serialization term N²·S/(M·BW) decreases with M
- t_queuing increases with M (denser mapping → more path intersections)

On a **healthy mesh** (H=1, t_queuing≈0): clear optimal M minimizing computation + communication.

On a **remapped mesh** (H>=1, t_queuing>=0): the optimal M shifts left (fewer PEs preferred). But with defects, you may not have the ideal defect-free mesh size available.

**The remapper's value proposition:** given a fixed defective substrate, the remapper lets you use **more cores** (larger M) to reduce computation, accepting higher H and some queuing — a trade-off that discard-based approaches cannot make, because they are stuck with whatever defect-free rectangle they find. The workload-aware cost function directly minimizes H and t_queuing for the chosen M.

*Use this model to: (a) explain U-shape in experimental results, (b) show where remapped performance sits relative to healthy optimal, (c) attribute performance gaps to specific terms (hop stretch vs queuing vs drain).*

### 6.2 Experimental Setup
- **Topologies:** Virtual 2D mesh sizes (64×64, 128×128, 256×256, 512×512); Physical mesh at 1.5× area with random faults.
- **Fault model:** PU faults ~7%, Router faults ~3.5%, Channel faults ~0.7% (based on Cerebras-class defect rates).
- **Workloads:** GEMM (systolic array), GEMV (broadcast+reduce).
- **Baselines:**
  - Healthy (no faults, ideal topology) — upper bound.
  - Defective without remapping (largest defect-free sub-mesh / discard) — a common baseline approach. (Note: Cerebras does perform remapping but has never disclosed their algorithm; we cannot use them as a direct baseline.)
  - Prior art: Zhang et al. (TVLSI 2009) topology reconfiguration (if reproducible at scale).

### 6.3 Algorithm Level: Mapping Quality
- Node cost (geometric displacement) and path cost (weighted hop count) vs. baselines.
- Utilization: fraction of healthy physical nodes used (ours vs. discard — this is the core value proposition).
- Visualization of mapping at representative scales (e.g., 64×64 on a faulty 96×96).

### 6.4 Workload Level: End-to-End Performance
- GEMM latency and throughput vs. healthy baseline and discard baseline.
- GEMV latency and throughput vs. healthy baseline and discard baseline.
- Breakdown: how much performance loss comes from longer hops vs. congestion vs. path stretch.
- *This is the "money figure" — show remapping recovers most of the healthy-baseline performance while using far more silicon than discard.*

### 6.5 Algorithm Level: Scalability
- Mapping time vs. mesh size (64×64 to 512×512).
- Memory footprint of the mapper at each scale.
- Compare scaling behavior: our hierarchical approach vs. SA (Zhang et al.) vs. exact (projected intractability).
- *Demonstrate near-linear scaling — this is a key differentiator.*

### 6.6 Architecture Level: Diagonal Link Utilization
- Mesh-to-DiagonalMesh remapping: performance improvement from exploiting 8-connected links.
- Comparison: regular mesh remapping (4-connected) vs. diagonal mesh remapping (8-connected) on the same faulty substrate.

### 6.7 Sensitivity Analysis (multi-dimensional, like Stratum)
- **Fault rate** (3%, 5%, 7%, 10%): how does mapping quality and workload performance degrade? — shows robustness.
- **Physical-to-virtual area ratio** (1.2×, 1.5×, 2.0×): how much spare area is needed? — shows the redundancy-utilization trade-off.
- **Mesh scale** (64² to 512²): does the approach maintain quality at scale? — shows scalability.
- **Workload type** (GEMM vs GEMV): does workload-aware cost actually help? — shows application specificity.

### 6.8 Architecture Level: Deadlock Freedom Verification
- CDG analysis: confirm acyclicity of channel dependency graph under submesh hierarchy routing for all experimental configurations.
- (Optional) Simulation-based verification: no deadlock observed in N million cycles.

### 6.9 Overhead Analysis (preempt reviewer concerns)
- **Mapping time:** one-time cost at boot/manufacturing — report wall-clock seconds/minutes per scale.
- **Routing table size:** memory per node for static routing tables.
- **Path stretch:** average and worst-case path length under submesh hierarchy routing vs. shortest path on same topology.
- **Throughput gap:** quantify remaining performance loss vs. healthy baseline and attribute it to specific causes (hop stretch, congestion, imperfect mapping).

---

## 7. Related Work (~1 page)

> MICRO convention: Related Work near the end, after Evaluation, so readers already understand your contributions.

### 7.1 Topology Reconfiguration for Defect Tolerance
- **Zhang et al. (DATE 2008, TVLSI 2009, DATE 2010):** Formalized the topology reconfiguration problem; proved NP-completeness; proposed simulated annealing (RRCS-gSA). Limited to <128 cores, topology-only cost, no routing guarantee.
- **Ke et al. (ASP-DAC 2012):** Hungarian algorithm for timing-similarity mapping. Elegant but O(N³) — not scalable to wafer-scale.
- **Ding et al. (TACO 2025):** Two-stage greedy column reconfiguration. Maximizes fault-free array but no workload awareness.
- **Qian et al. (JPDC 2024):** Greedy-memetic algorithm. Improved scalability over SA but still no workflow or routing co-optimization.

### 7.2 Deadlock-Free Routing on Irregular/Faulty Topologies
- **Foundational:** Dally & Seitz (1987) CDG formalism; Glass & Ni (1994) Turn Model; Duato (1993/1995) escape sub-network theory.
- **ARIADNE (PACT 2011):** Topology-agnostic reconfiguration with up*/down* routing. Handles arbitrary faults but up*/down* limits path diversity.
- **uDIREC (MICRO 2013):** Unified diagnosis + reconfiguration with MOUNT routing. Most comprehensive prior work on fault-tolerant deadlock-free routing, but no virtual topology abstraction or workload-specific optimization.
- **Vicis (DATE 2009):** Two-level fault tolerance; handles up to 50% router failures but no topology remapping.

### 7.3 Task Graph Mapping on Faulty NoC
- Hu & Marculescu (TCAD 2005), Kadri & Koudil survey (2019), and others.
- Focus on task-to-PE assignment, not topology remapping. Small scale (<64 cores). No deadlock-free routing on post-fault irregular topologies.

### 7.4 Wafer-Scale and Chiplet Defect Tolerance
- **Cerebras WSE (Hot Chips 2019, IEEE Micro 2024, SIGOPS 2025):** Hardware redundancy + software remapping to restore regular mesh. Does not optimize for workload or exploit diagonal links.
- **AMD MI300 series:** Chiplet-level redundancy (spare XCDs/CUs). Effective at chiplet granularity but not at core/router level.

### 7.5 NPU Virtualization
- **vNPU (ISCA 2025):** Virtual topology creation with best-effort mapping for NPUs. Closest in spirit but targets NPU partitioning, not defect-tolerant remapping on 2D mesh.
- **NPU Virtualization (MICRO 2024):** Hardware-assisted virtualization for cloud NPU sharing.

### 7.6 Virtual Network Embedding (VNE)
- Cloud/datacenter context (Zhu & Ammar 2006, Chowdhury et al. 2009, Fischer et al. 2013). NP-hard (Rost & Schmid 2020). Different objective (revenue, multi-tenant) and no hardware defect/deadlock constraints.

---

## 8. Discussion (~0.5 page)

### 8.1 Limitations
- Current implementation is offline (mapping computed before execution, not at runtime).
- Evaluated on synthetic fault patterns; real wafer defect maps may have spatial correlation (clustering).
- Cost model assumes static workloads; dynamic or irregular workloads not yet supported.
- Submesh hierarchy routing may introduce path stretch compared to optimal shortest paths.

### 8.2 Future Work
- **Online/incremental remapping:** handle faults discovered at runtime (aging, transient faults).
- **Non-mesh virtual topologies:** extend to torus, hypercube, or application-specific topologies.
- **Real hardware integration:** Cerebras SDK, chiplet platform validation.
- **Heterogeneous defects:** model routers with degraded (not binary) performance.

---

## 9. Conclusion (~0.25 page)

- Restate the problem: defect tolerance for large-scale 2D mesh architectures requires topology remapping, not just redundancy.
- Restate the solution: model-defined remapper with hierarchical mapping, workload-aware cost, and deadlock-free routing.
- Restate key results: (fill in quantitative highlights).
- Closing statement: as chips scale to wafer-level integration, software-defined topology remapping becomes essential — our framework provides the algorithmic foundation.

---

## Page Budget Estimate

| Section | Pages |
|---------|-------|
| 1. Introduction | 1.25 |
| 2. Background & Motivation | 1.25 |
| 3. Challenges | 0.5 |
| 4. Design | 2.5 |
| 5. Implementation | 0.5 |
| 6. Evaluation (incl. analytical model) | 3.25 |
| 7. Related Work | 1.0 |
| 8. Discussion | 0.5 |
| 9. Conclusion | 0.25 |
| **Total** | **~11** |

> **Note:** Evaluation expanded to 3 pages to accommodate multi-level evaluation structure and overhead analysis (learned from Stratum/MICRO '25 review expectations). Trimmed Introduction and Challenges slightly to compensate.

---

## Corrections & Notes on Original Outline

### On Clos manufacturing (your point 1.iv)
Your intuition is correct but the reason is more specific than "extra resources." Clos requires **multi-stage switching with non-local, non-planar interconnects** — the middle-stage switches must connect to *every* input and output stage, requiring long cross-chip wires that don't match the nearest-neighbor wiring natural to 2D lithography. It's a fundamental layout mismatch, not just a resource overhead.

### On Ullmann/VF2/VF3 (your point 3.i)
You are correct — these are impractical for large-scale NoC. Ullmann (1976) has worst-case O(n!·m^n). VF2 (2004) and VF3 (2017) improve pruning but remain exponential; they are designed for and benchmarked on graphs with ≤10K nodes. At 512×512 = 262,144 nodes, they are completely intractable. Our hierarchical decomposition is well-motivated.

### On "broadcast storm" / infinite duplication (your point 3.iii)
Three distinct routing hazards on irregular topologies: (a) **deadlock** from cyclic channel dependencies in the CDG, (b) **infinite duplication (unicast)** when a routing path visits the same node twice — the stateless routing table at that node encodes output ports for both visits, so every arrival fans out to all ports, creating copies that cycle and duplicate exponentially, and (c) **multicast amplification** when multicast branches intersect, compounding the duplication. Notably, (b) means broadcast-storm-like behavior is not limited to multicast — it affects unicast too if paths contain node-revisit cycles.

### On MICRO-specific sections (your point 5)
MICRO papers typically include: **Evaluation** (the largest section — reviewers want thorough experimental evidence), **Related Work** (positioned after evaluation so readers understand your contributions first), **Discussion** (limitations + future work — shows intellectual honesty), and **Conclusion** (brief, no new information). I've included all of these above. MICRO does *not* require a separate "Outlook" section — fold that into Discussion.

---

## Background Writing Notes (merged from paper_outline.md)

> These are draft-quality narrative notes for writing the actual paper sections. Cross-reference with `reference/*.md` files for detailed citations.

### Defects Are Inevitable (for §2.1.1)

Semiconductor defects follow a bathtub curve: high infant mortality, a stable useful-life period, then increasing wear-out failures. Critically, as devices age, defect rates rise — components that pass initial screening may still develop faults over their operational lifetime. Combined with shrinking process nodes and growing die/wafer areas, the probability of at least one defect per chip approaches certainty. Designers must plan for defects, not hope to avoid them.

- Reference: https://testflowinc.com/blog/semiconductor-defect-rate-bathtub-curve

### Topology-Aware Computing Depends on Regularity (for §2.2, formerly §2.3)

High-performance kernels (GEMM on systolic arrays, GEMV with broadcast+reduce, collective communications) are designed around **regular topologies** — they exploit predictable hop counts, uniform bandwidth, and symmetric routing to schedule data movement and balance load. A regular topology allows the compiler/runtime to reason about latency and throughput more effectively.

### Redundancy: Industry Examples (for §2.1.2)

To maintain regularity despite inevitable defects, chip designers provision **spare components** and remap defective units to healthy ones, exposing an ideal topology to software:

- **AMD MI250X/MI300X:** Each compute die has 2 extra Compute Units (CUs) disabled for yield (112→110 per GCD on MI250X, 40→38 per XCD on MI300X). Software sees a uniform CU count regardless of which units are harvested. (ref: `reference/AMD_MI_Series_Redundancy.md`)
- **Cerebras WSE-3:** 970K physical cores, 900K active (~7% spare). Defective cores are locally replaced; the 2D mesh fabric reroutes around them transparently. (ref: `reference/Cerebras_WSE_Redundancy.md`)

### Symmetric vs. Asymmetric Recovery (archived from old §2.4, may go in §3 or §7)

**Symmetric topologies (e.g., Clos networks):** Fault tolerance is straightforward. All middle-stage switches are functionally interchangeable — losing one reduces path diversity but not connectivity. The topology is acyclic, so conflicts cause congestion, never deadlock. Recovery is just graph recoloring (polynomial time). (ref: `reference/Clos_Network_Fault_Tolerance.md`)

**Asymmetric topologies (e.g., 2D mesh):** Every node is topologically unique. Removing a defective node creates an irregular "hole" that:
- Breaks routing assumptions (e.g., dimension-order routing may no longer work)
- Can introduce cyclic dependencies → **deadlock**
- Requires non-trivial remapping to restore a usable virtual topology

### The Hidden Cost of Redundancy (for §2.1.3)

Current redundancy schemes hide unused spare components after remapping:
- **Spare routers and links** that are not on any active path are powered down or ignored.
- **Diagonal links** (e.g., in Cerebras WSE) exist in hardware but are not exposed in the virtual 2D mesh topology. These could provide extra routing bandwidth for memory-bound workloads.
- **Spare processing units** that survive defect replacement sit idle.

**Motivation:** Rather than hiding these resources, we want to **expose and utilize them** — turning redundancy overhead into a performance advantage.

### Challenges Detail (for §3)

Exposing spare components creates an **irregular topology**, which raises several hard questions:

1. **NP-hardness:** Even isomorphic subgraph matching — the simplest form of topology mapping — is NP-complete [Karp 1972]. Approximate or relaxed mappings add further degrees of freedom but do not escape the fundamental combinatorial complexity. (ref: `reference/Subgraph_Isomorphism_NP_Hard.md`)
2. **Quality evaluation:** How do we measure whether a given remapping is good? Metrics must capture communication cost, load balance, and workload-specific performance (e.g., systolic array efficiency).
3. **Deadlock freedom:** Rerouting around defective nodes, routers, and channels on an irregular topology can introduce cyclic dependencies in the routing. How can we guarantee deadlock-free routing under arbitrary defect patterns?

### Why Not Other Topologies? (for §2.3, extend Clos discussion)

#### Fully-Connected (All-to-All)
- Trivial for routing (1 hop to anywhere)
- Works for small core counts (e.g., AMD MI300 with ~8 XCDs)
- **BUT:** Not scalable:
  - O(N^2) links — unaffordable for large-scale chips (hundreds/thousands of cores)
  - Wire length and area grow quadratically

#### Our Target: Large-Scale 2D Topologies
- Manufacturing-friendly (planar layout), scalable (O(N) links), matches physical substrate
- Where our work has most impact: asymmetric and large-scale topologies (Cerebras-class), chiplet interposers with 2D NoC

### Experiment Coverage Summary

| Experiment | Virtual Topology | Physical Topology | Purpose |
|------------|-----------------|-------------------|---------|
| MeshScaling | 2D Mesh (various sizes) | 2D Mesh (1.5x, faults) | Scalability analysis |
| RemappedExperiment | 2D Mesh (256, 512) | 2D Mesh (1.5x, faults) | Main defect tolerance eval |
| Diagonal mapping | 2D Mesh | 8-connected Diagonal Mesh (faults) | Unused routing resource utilization |
