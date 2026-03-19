# Paper Structure: Model-Defined Remapper (MICRO 2026)

> Target: 11 pages, double-column, double-blind.
> MICRO recommended flow: Introduction → Background → Design → Implementation → Evaluation → Related Work → Conclusion.

---

## 1. Introduction (~1.5 pages)

Hook → Problem → Insight → Contributions → Results snapshot.

- **Hook:** Large-scale 2D mesh architectures (wafer-scale chips, chiplet interposers) are the dominant substrate for high-performance computing, but manufacturing defects are inevitable — and worsen with scale and aging.
- **Current mitigations and their costs:**
  - Hardware redundancy (spare cores/links): fixed at design time, wastes area/power, and may be insufficient at high defect rates (e.g., Cerebras WSE reserves ~1–7% spare cores).
  - Software discard (use largest defect-free sub-mesh): abandons usable-but-irregular silicon.
- **Industrial evidence of the need:** Cerebras confirms software-level remapping to restore regular mesh \cite{cerebras2025sigops}, and a Cerebras co-authored paper states "a proprietary process will route around [defects]" \cite{luczynski2024reduce} — but the algorithm is undisclosed. Defect-tolerant remapping is industrially critical yet remains an open problem in the literature.
- **The gap:** High-performance kernels (GEMM, GEMV) require regular topology, but no existing approach efficiently remaps an irregular/faulty physical mesh into a virtual regular one at scale with deadlock-free routing guarantees.
- **Our insight:** Decouple virtual topology from physical topology via a *model-defined remapper* — applications see a regular mesh while the remapper transparently maps it onto all healthy resources in a defective physical substrate.
- **Contributions** (4 bullets, one sentence each):
  1. A hierarchical virtual-to-physical topology remapping framework that scales to 512×512 meshes.
  2. A deadlock-free routing scheme for irregular post-remapping topologies via submesh hierarchy routing.
  3. Exploitation of underutilized routing resources (diagonal links) through cross-topology remapping.
  4. Comprehensive evaluation across scales, fault rates, and workloads (GEMM, GEMV).
- **Results teaser:** Key quantitative highlights (fill in after experiments finalize).

---

## 2. Background & Motivation (~1.5 pages)

### 2.1 Defects Are Inevitable
- Semiconductor defect bathtub curve: early-life (infant mortality) + wear-out (aging/electromigration).
- At wafer scale, defect probability per chip approaches 1 — defect tolerance is not optional, it is a design requirement.

### 2.2 Regular Topology Is a Software Requirement
- High-performance kernels (systolic GEMM, broadcast+reduce GEMV) are designed for regular 2D mesh:
  - Uniform neighbor count enables systolic dataflow.
  - Dimension-order routing gives deterministic latency.
  - Programming models assume a clean coordinate space.

### 2.3 Symmetric vs. Asymmetric Topologies
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

### 2.4 Industry Practice: Spare Cores and Yield Binning
Modern chips universally over-provision and disable defective units. Concrete examples:

**GPUs (SM/CU harvesting — yield binning to lower SKUs):**
| Die | Full Die | Top SKU (enabled) | Disabled | Source |
|-----|----------|-------------------|----------|--------|
| NVIDIA GA102 | 84 SMs | RTX 3090: 82 SMs | 2 (2.4%) | NVIDIA Ampere Whitepaper |
| NVIDIA AD102 | 144 SMs | RTX 4090: 128 SMs | 16 (11%) | TechPowerUp |
| NVIDIA GH100 | 144 SMs | H100 SXM: 132 SMs | 12 (8.3%) | NVIDIA Hopper Architecture |
| AMD Navi 31 | 96 CUs | RX 7900 XTX: 96 CUs; 7900 XT: 84 CUs | 0–12 | Tom's Hardware |

**CPUs (core harvesting):**
| Die | Full Die | Harvested SKU | Disabled | Source |
|-----|----------|---------------|----------|--------|
| AMD Zen 3 CCD | 8 cores | Ryzen 5 5600X: 6 cores | 2 (25%) | AnandTech |
| Intel Sapphire Rapids tile | ~15 cores | Xeon: 14 cores | 1 (~7%) | WikiChip |

**Accelerators (spare cores with routing):**
| Product | Physical | Enabled | Spare | Source |
|---------|----------|---------|-------|--------|
| Cerebras WSE-1 | ~406K cores | 400K | ~1.5% | Cerebras blog |
| Tesla Dojo D1 | 360 cores | 354 | 6 (1.7%) | Hot Chips 34 |

**Two strategies emerge:**
1. **Discard/bin** (GPUs, CPUs): over-provision, fuse off defects, sell as lower SKU. No topology change — the remaining units are independent (GPU SMs) or connected via crossbar, so disabling units doesn't create an irregular topology.
2. **Spare + remap** (Cerebras, Dojo): small spare pool (~1–2%), reconfigure routing to bypass faults. Required because cores are mesh-connected — disabling a core creates a hole in the topology.

**Key observation:** Discard/bin works when units are independent or crossbar-connected (GPUs, CPUs). It fails for **mesh-connected** architectures where a disabled interior node creates an irregular topology that breaks dimension-order routing.

### 2.5 Limitations of Current Approaches
| Approach | Mechanism | Limitation |
|----------|-----------|------------|
| Yield binning (NVIDIA, AMD, Intel) | Over-provision, fuse off defective SMs/CUs/cores, sell as lower SKU | Only works for independent/crossbar-connected units; not applicable to mesh-connected architectures |
| Spare cores + proprietary remap (Cerebras WSE) | ~1.5% spare cores; undisclosed algorithm routes around defects \cite{luczynski2024reduce, cerebras2025sigops} | Algorithm not published; cannot be reproduced, analyzed, or extended by the community |
| Software discard | Use largest defect-free rectangular sub-mesh | Abandons healthy-but-irregular silicon; utilization drops sharply at higher defect rates |
| Topology reconfiguration (Zhang et al.) | Remap virtual mesh onto faulty physical mesh | Small scale (<128), no workload awareness, no routing guarantee |

### 2.5 Quantifying the Cost of Discard

> **TODO: Derive a model for the expected largest defect-free k×k sub-mesh in an N×N grid given i.i.d. defect probability p.**
>
> Goal: show a curve of **max defect-free mesh size vs. defect rate** (e.g., for N=512).
> - At p=1%, largest defect-free sub-mesh ≈ ?×?
> - At p=5%, ≈ ?×?
> - At p=10%, ≈ ?×?
>
> Expected result: the largest defect-free rectangle shrinks rapidly with p, meaning the discard approach wastes most of the healthy silicon even at moderate defect rates.
>
> This replaces the vague "utilization drops sharply" claim in §2.4 with a concrete, quantitative argument. Should include:
> 1. Analytical model or probabilistic bound (related to geometric distribution / longest run in 2D)
> 2. Monte Carlo validation (generate random defect maps, measure largest defect-free rectangle)
> 3. A figure: x-axis = defect rate, y-axis = max sub-mesh size / total mesh size (utilization)
> 4. Compare: utilization under discard vs. utilization under remapping (our approach uses ALL healthy nodes)
>
> This is the **quantitative motivation** for the entire paper — make the gap between discard and remapping visually obvious.

### 2.6 Our Goal
Remap a virtual regular mesh onto *all* healthy nodes of a faulty physical mesh — preserving the regular programming model while maximizing utilization, optimizing for the target workload, and guaranteeing deadlock-free routing.

---

## 3. Challenges (~0.75 page)

> **Structural note:** Each challenge below maps 1:1 to a design component in §4. This makes each design decision feel motivated by a concrete, named problem.

### 3.1 Scalability → addressed by §4.2 Hierarchical Spatial Search
- The remapping problem is a constrained subgraph isomorphism variant → NP-hard.
- Exact algorithms (Ullmann 1976, VF2 2004, VF3 2017) have exponential worst-case complexity. They work well for small pattern graphs (tens of nodes) but are completely intractable for meshes with 10K–260K+ nodes.
  - *Ullmann:* backtracking with refinement; O(n! · m^n) worst case.
  - *VF2/VF3:* state-space search with pruning; still exponential, designed for graphs with ≤10K nodes in practice.
- Simulated annealing (Zhang et al. TVLSI 2009) and memetic algorithms (Qian et al. 2024) improve over exact methods but remain too slow at wafer scale due to their iterative global search.
- **Need:** a hierarchical heuristic that decomposes the problem spatially for near-linear scaling.

### 3.2 Application Specificity → addressed by §4.3 Workload-Aware Cost Function
- Topology-only cost metrics (minimize total hop count) ignore the actual workload.
- If two virtual nodes never communicate, their physical distance is irrelevant.
- GEMM (systolic) has strict nearest-neighbor communication; GEMV (broadcast+reduce) has a different pattern with long-range collective operations.
- **Need:** a workload-aware cost function that weights mapping quality by actual communication volume.

### 3.3 Routing Correctness → addressed by §4.4–4.5 Static Routing + Submesh Hierarchy
- **Deadlock:** Intersecting routing paths can create cyclic *channel* dependencies in the CDG → messages block forever waiting for each other.
- **Infinite duplication (even for unicast):** If a routing path visits the same physical node twice (a cycle in the *path*, not the CDG), the stateless static routing table at that node cannot distinguish first visit from second. Since it must encode output ports for both visits, every arrival fans out to all ports → the cycle produces copies that return and fan out again → exponential duplication, never terminates. This is the same mechanism as a broadcast storm but triggered by path cycles, not multicast fan-out.
- **Multicast amplification:** For multicast operations (e.g., GEMV broadcast/reduce), the problem compounds — branch intersection at a router duplicates flits from converging branches, each of which may themselves cycle.
- On an irregular post-remapping topology, standard dimension-order routing (XY) may not be applicable — some XY paths may traverse faulty nodes.
- **Need:** a routing scheme that (a) finds valid physical paths for all virtual communications, (b) guarantees acyclic CDG (deadlock freedom), and (c) guarantees cycle-free paths per node (no node visited twice) to prevent infinite duplication.

---

## 4. Design: Model-Defined Remapper (~2.5 pages)

### 4.1 Overview
- System architecture diagram: Virtual topology → Remapper → Physical topology + Routing tables.
- Three-phase pipeline: **Node Mapping → Path Routing → Deadlock Resolution**.

### 4.2 Node Mapping: Hierarchical Spatial Search
- **Problem formulation:** Given virtual mesh V and faulty physical mesh P (with defective nodes/links removed), find an injective mapping f: V → P that minimizes a workload-weighted cost.
- **Approximate graph matching**, not exact isomorphism — we optimize a continuous cost function rather than requiring strict structural preservation.
- **Phase 1 — Spatial decomposition:**
  - Recursive Coordinate Bisection (RCB) partitions both V and P into aligned spatial regions.
  - Reduces global NxN assignment to a set of local sub-problems.
- **Phase 2 — Coarse mapping via KdTree super nodes:**
  - Build KdTree over physical nodes; group into super nodes.
  - Match virtual partitions to physical super nodes by spatial proximity.
- **Phase 3 — Fine mapping via frontier expansion:**
  - Within each partition, expand mapping frontier outward from seed nodes.
  - 2-level hierarchical candidate search: coarse (super node) then fine (individual node).
  - Parallel candidate evaluation (rayon) for throughput.
  - **Frontier-based expansion avoids the local minima of pure greedy assignment** — each new mapping decision is informed by the spatial context of already-mapped neighbors.

### 4.3 Workload-Aware Cost Function
- **Coordinate cost:** geometric displacement between virtual and physical positions (RANSAC-based geometric consistency check).
- **Hop cost:** weighted by link usage (LinkUsage tracking) — penalizes mappings that overload physical links.
- **Communication cost:** weighted by actual traffic volume from the workload graph (GEMM/GEMV IR).
  - If two nodes never communicate → zero cost regardless of physical distance.
  - High-traffic links → heavily penalized if mapped to long physical paths.

### 4.4 Static Deterministic Routing
- For each virtual communication edge, compute a physical routing path on the mapped topology.
- Paths are static (computed once at mapping time) and deterministic (same path every time).
- **Why static:** enables offline analysis of channel dependencies and eliminates runtime routing overhead.

### 4.5 Deadlock-Free Routing via Submesh Hierarchy
- **Problem:** arbitrary physical paths on an irregular topology can create cycles in the channel dependency graph (CDG).
- **Solution:** Submesh hierarchy routing with *ascend-then-descend* constraint:
  - Partition the mapped physical mesh into a hierarchy of submeshes.
  - Each routing path first ascends the hierarchy (coarse submeshes), then descends (fine submeshes).
  - **No re-ascent allowed** → the hierarchical ordering imposes a total order on channel usage → acyclic CDG → deadlock freedom.
- **Broadcast storm prevention:** deterministic, non-duplicating forwarding — each message follows exactly one path.
- Works for both 4-connected (standard mesh) and 8-connected (diagonal mesh) topologies.
- **Hardware requirement: ≥2 virtual channels (VCs).** The submesh hierarchy routing uses separate VCs for ascending and descending phases to guarantee deadlock freedom. This is a conservative assumption — modern architectures with true (general-purpose, reassignable) VCs provide far more:
  - Cerebras WSE: **24 colors** — true VCs, any color can carry any data, non-blocking, time-multiplexed on same physical link \cite{cerebras2024sdk}
  - Google TPU ICI: **≥2 VCs** for dateline-based deadlock-free torus routing
  - Cray T3D/T3E, IBM Blue Gene/L: **2 VCs** — the historical minimum for deadlock-free torus routing
  - Note: Intel mesh (AD/AK/BL/IV rings) and ARM CHI (REQ/RSP/SNP/DAT) use protocol-level virtual *networks*, not true VCs — each network is dedicated to a specific message class and cannot be reassigned for routing. These are not applicable to our argument.
  - Li et al. (ISCA 2024) prove that all practical coherence protocols require ≥2 virtual networks for deadlock freedom \cite{li2024minvn}.
  - AMD Infinity Fabric: proprietary, VC count undisclosed (likely ≥2 but unconfirmed). NVIDIA GPU: uses crossbar internally, not mesh — VCs not applicable.
  - **Adversary case (address proactively in paper):** Real VC-free mesh products exist — Kalray MPPA-256 (turn-model, single die), Tilera TILE-Gx (5 physical nets, single die), Adapteva Epiphany (3 physical nets, multi-chip extensible), SpiNNaker (packet-dropping, 1M cores). But: single-die products discard the entire die on interior defects. Adapteva designed a multi-chip extensible mesh without VCs but **never solved** the hole-in-mesh problem when a chip dies. SpiNNaker tolerates packet loss (unacceptable for deterministic compute). The only products that handle interior defects in multi-die meshes losslessly (Cerebras 24 VCs, TPU ≥2 VCs) all use virtual channels. **≥2 VCs is the inherent cost of remapping over waste.**
  - See `reference/Virtual_Channels_in_Modern_Hardware.md` for full details and citations.

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

Establish a latency model to frame the experimental results and explain the remapper's trade-off.

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

### Defects Are Inevitable (for §2.1)

Semiconductor defects follow a bathtub curve: high infant mortality, a stable useful-life period, then increasing wear-out failures. Critically, as devices age, defect rates rise — components that pass initial screening may still develop faults over their operational lifetime. Combined with shrinking process nodes and growing die/wafer areas, the probability of at least one defect per chip approaches certainty. Designers must plan for defects, not hope to avoid them.

- Reference: https://testflowinc.com/blog/semiconductor-defect-rate-bathtub-curve

### Topology-Aware Computing Depends on Regularity (for §2.2)

High-performance kernels (GEMM on systolic arrays, GEMV with broadcast+reduce, collective communications) are designed around **regular topologies** — they exploit predictable hop counts, uniform bandwidth, and symmetric routing to schedule data movement and balance load. A regular topology allows the compiler/runtime to reason about latency and throughput more effectively.

### Redundancy: Industry Examples (for §2.4)

To maintain regularity despite inevitable defects, chip designers provision **spare components** and remap defective units to healthy ones, exposing an ideal topology to software:

- **AMD MI250X/MI300X:** Each compute die has 2 extra Compute Units (CUs) disabled for yield (112→110 per GCD on MI250X, 40→38 per XCD on MI300X). Software sees a uniform CU count regardless of which units are harvested. (ref: `reference/AMD_MI_Series_Redundancy.md`)
- **Cerebras WSE-3:** 970K physical cores, 900K active (~7% spare). Defective cores are locally replaced; the 2D mesh fabric reroutes around them transparently. (ref: `reference/Cerebras_WSE_Redundancy.md`)

### Symmetric vs. Asymmetric Recovery (for §2.3)

**Symmetric topologies (e.g., Clos networks):** Fault tolerance is straightforward. All middle-stage switches are functionally interchangeable — losing one reduces path diversity but not connectivity. The topology is acyclic, so conflicts cause congestion, never deadlock. Recovery is just graph recoloring (polynomial time). (ref: `reference/Clos_Network_Fault_Tolerance.md`)

**Asymmetric topologies (e.g., 2D mesh):** Every node is topologically unique. Removing a defective node creates an irregular "hole" that:
- Breaks routing assumptions (e.g., dimension-order routing may no longer work)
- Can introduce cyclic dependencies → **deadlock**
- Requires non-trivial remapping to restore a usable virtual topology

### The Hidden Cost of Redundancy (for §2.5)

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
