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

### 2.4 Limitations of Current Approaches
| Approach | Mechanism | Limitation |
|----------|-----------|------------|
| Hardware redundancy (AMD MI300, Cerebras WSE) | Spare cores/links swapped in at manufacturing/boot | Fixed overhead; diagonal links wasted when only regular mesh exposed |
| Software discard | Use largest defect-free rectangular sub-mesh | Abandons healthy-but-irregular silicon; utilization drops sharply at higher defect rates |
| Topology reconfiguration (Zhang et al.) | Remap virtual mesh onto faulty physical mesh | Small scale (<128), no workload awareness, no routing guarantee |

### 2.5 Our Goal
Remap a virtual regular mesh onto *all* healthy nodes of a faulty physical mesh — preserving the regular programming model while maximizing utilization, optimizing for the target workload, and guaranteeing deadlock-free routing.

---

## 3. Challenges (~0.75 page)

### 3.1 Scalability
- The remapping problem is a constrained subgraph isomorphism variant → NP-hard.
- Exact algorithms (Ullmann 1976, VF2 2004, VF3 2017) have exponential worst-case complexity. They work well for small pattern graphs (tens of nodes) but are completely intractable for meshes with 10K–260K+ nodes.
  - *Ullmann:* backtracking with refinement; O(n! · m^n) worst case.
  - *VF2/VF3:* state-space search with pruning; still exponential, designed for graphs with ≤10K nodes in practice.
- Simulated annealing (Zhang et al. TVLSI 2009) and memetic algorithms (Qian et al. 2024) improve over exact methods but remain too slow at wafer scale due to their iterative global search.
- **Need:** a hierarchical heuristic that decomposes the problem spatially for near-linear scaling.

### 3.2 Application Specificity
- Topology-only cost metrics (minimize total hop count) ignore the actual workload.
- If two virtual nodes never communicate, their physical distance is irrelevant.
- GEMM (systolic) has strict nearest-neighbor communication; GEMV (broadcast+reduce) has a different pattern with long-range collective operations.
- **Need:** a workload-aware cost function that weights mapping quality by actual communication volume.

### 3.3 Routing Correctness
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

---

## 5. Implementation (~0.5 page)

- Implemented in Rust (workspace: Common, Util, IR, NoC, Mapper, Simulator, Experiments).
- Parallel evaluation via rayon; light-weight mesh representation for large scales (flat arrays instead of Rc/RefCell for 512×512+).
- Workload IR: task/work abstractions encoding GEMM (systolic) and GEMV (broadcast+reduce) communication patterns.
- Latency predictor with congestion awareness for cost evaluation.
- Configuration: bandwidth, FLOPS, latencies, fault rates, mapper parameters (candidate pool size, RANSAC iterations, etc.).

---

## 6. Evaluation (~2.5 pages)

### 6.1 Experimental Setup
- **Topologies:** Virtual 2D mesh sizes (64×64, 128×128, 256×256, 512×512); Physical mesh at 1.5× area with random faults.
- **Fault model:** PU faults ~7%, Router faults ~3.5%, Channel faults ~0.7% (based on Cerebras-class defect rates).
- **Workloads:** GEMM (systolic array), GEMV (broadcast+reduce).
- **Baselines:**
  - Healthy (no faults, ideal topology).
  - Defective without remapping (largest defect-free sub-mesh / discard).
  - Prior art: Zhang et al. (TVLSI 2009) topology reconfiguration (if reproducible at scale).

### 6.2 Mapping Quality
- Node cost (geometric displacement) and path cost (weighted hop count) vs. baselines.
- Utilization: fraction of healthy physical nodes used.
- Visualization of mapping at representative scales (e.g., 64×64 on a faulty 96×96).

### 6.3 Workload Performance
- GEMM latency and throughput vs. healthy baseline and discard baseline.
- GEMV latency and throughput vs. healthy baseline and discard baseline.
- Breakdown: how much performance loss comes from longer hops vs. congestion.

### 6.4 Scalability
- Mapping time vs. mesh size (64×64 to 512×512).
- Compare scaling behavior: our hierarchical approach vs. SA (Zhang et al.) vs. exact (projected intractability).

### 6.5 Diagonal Link Utilization
- Mesh-to-DiagonalMesh remapping: performance improvement from exploiting 8-connected links.
- Comparison: regular mesh remapping (4-connected) vs. diagonal mesh remapping (8-connected) on the same faulty substrate.

### 6.6 Sensitivity Analysis
- Varying fault rates: how does mapping quality and workload performance degrade?
- Varying physical-to-virtual area ratio (1.2×, 1.5×, 2.0×).
- (Optional) Varying workload communication patterns.

### 6.7 Deadlock Freedom Verification
- CDG analysis: confirm acyclicity of channel dependency graph under submesh hierarchy routing for all experimental configurations.
- (Optional) Simulation-based verification: no deadlock observed in N million cycles.

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
| 1. Introduction | 1.5 |
| 2. Background & Motivation | 1.5 |
| 3. Challenges | 0.75 |
| 4. Design | 2.5 |
| 5. Implementation | 0.5 |
| 6. Evaluation | 2.5 |
| 7. Related Work | 1.0 |
| 8. Discussion | 0.5 |
| 9. Conclusion | 0.25 |
| **Total** | **~11** |

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
