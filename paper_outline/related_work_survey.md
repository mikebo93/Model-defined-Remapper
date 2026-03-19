# Related Work Survey: Topology Remapping, Defect Tolerance, and Deadlock-Free Routing

## Summary & Gap Analysis

**Our claim: No prior work addresses all of the following simultaneously:**
1. Large-scale (100s-1000s of cores) virtual-to-physical topology remapping
2. Workload-specific (GEMM, GEMV) mapping optimization
3. Deadlock-free routing on the resulting irregular topology
4. Defect tolerance across cores, routers, AND links

The closest related works are the **topology reconfiguration** papers by Zhang et al. (2008-2010) and the **ARIADNE/uDIREC** fault-tolerance frameworks, but they differ in key ways (see analysis below).

---

## Category 1: Virtual Network Embedding (VNE) — Different Objective

VNE maps virtual networks onto substrate networks in cloud/datacenter contexts. The problem is related but has different objectives (revenue maximization, multi-tenant sharing) and does not address hardware defects or deadlock-free routing.

| Paper | Venue/Year | Key Contribution | Relevance to Us |
|-------|-----------|------------------|-----------------|
| Zhu & Ammar, "Algorithms for Assigning Substrate Network Resources to Virtual Network Components" | INFOCOM 2006 | Early formal treatment of VNE problem with heuristics | Problem formulation reference; different objective (cloud resource allocation) |
| Yu et al., "Rethinking Virtual Network Embedding: Substrate Support for Path Splitting and Migration" | SIGCOMM CCR 2008 | Path splitting and migration for VNE | Concept of substrate flexibility; not hardware-level |
| Chowdhury et al., "ViNEYard: Virtual Network Embedding with Coordinated Node and Link Mapping" | INFOCOM 2009 / ToN 2012 | MIP formulation, D-ViNE/R-ViNE algorithms | Coordinated node+link mapping idea; cloud-scale, not chip-scale |
| Fischer et al., "Virtual Network Embedding: A Survey" | IEEE Comm. Surveys & Tutorials 2013 | Comprehensive VNE taxonomy and survey | Background reference for embedding problem classification |
| Rost & Schmid, "On the Computational Complexity of VNE" | IFIP Networking 2016 | Proved strong NP-hardness even for restricted graphs | Complexity reference — our problem is at least as hard |
| Rost & Schmid, "On the Hardness and Inapproximability of VNE" | IEEE/ACM ToN 2020 | Proved VNE optimization is inapproximable | Justifies heuristic approach |
| Figiel et al., "Optimal VNE for Tree Topologies" | ACM SPAA 2021 | FPT algorithm for tree substrates | Shows exact solutions possible for restricted topologies only |

**Gap:** VNE literature focuses on cloud/datacenter virtual networks, not hardware-level NoC with physical defects and deadlock constraints.

---

## Category 2: Task Graph Mapping on Faulty NoC

These map application task graphs onto NoC tiles. Closer to our work but typically: (a) small scale (<64 cores), (b) focus on task-to-PE assignment not topology remapping, (c) don't address routing deadlock on irregular post-fault topologies.

| Paper | Venue/Year | Key Contribution | Relevance / Gap |
|-------|-----------|------------------|-----------------|
| Hu & Marculescu, "Energy- and Performance-Aware Mapping for Regular NoC Architectures" | IEEE TCAD 2005 | Branch-and-bound mapping of IP cores onto mesh NoC | Foundational NoC mapping; assumes healthy topology |
| Derin et al., "Online Task Remapping Strategies for Fault-Tolerant NoC Multiprocessors" | ACM/IEEE NoCS 2011 | ILP + heuristics for task remapping upon PE failure | Online remapping but small scale, no deadlock-free routing |
| Bayar et al., "Route-Aware Task Mapping for Fault-Tolerant 2D-Mesh NoC" | IEEE DTIS 2011 | GA-based joint mapping+routing for faulty mesh | Considers routing overlap but not deadlock freedom |
| Khalili et al., "A Fault-Tolerant Core Mapping Technique in NoCs" | IET CDT 2013 | Dynamic spare core placement based on application vulnerability | Spare-based; doesn't remap topology |
| Rohbani et al., "Energy-Efficient Fault-Aware Core Mapping in Mesh-Based NoC" | J. Network & Computer Applications 2017 | Functional metrics (NAD, PVR, WCE) for fault-aware mapping | Per-task mapping, not topology virtualization |
| Kadri & Koudil, "Survey on Fault-Tolerant Application Mapping for NoC" | J. Systems Architecture 2019 | Survey: mapping+routing, redundancy, remapping approaches | Confirms no unified solution for large-scale |
| Agyeman et al., "Fault-Tolerant NoC with Flexible Spare Core Placement" | ACM JETC 2018 | ILP/PSO spare core placement for mesh NoC | Fixed spare allocation; doesn't utilize all healthy nodes |
| Pourmohseni et al., "Hard Real-Time Application Mapping Reconfiguration for NoC" | Real-Time Systems 2019 | Bounded worst-case reconfiguration latency | Real-time focus; small scale |
| RL-based fault-tolerant mapping (Transformer + RL) | Discover Computing 2025 | AI-driven fault-tolerant mapping | Latest approach; still task-to-PE, not topology remapping |

**Gap:** Task mapping works assign tasks to PEs but don't remap the entire virtual topology onto a larger faulty physical mesh. They don't scale to 100s of cores or address deadlock-free routing.

---

## Category 3: Topology Reconfiguration for Defect Tolerance — CLOSEST RELATED WORK

These are the most directly related papers. They reconfigure the NoC topology to present a unified view despite defects.

| Paper | Venue/Year | Key Contribution | Relevance / Gap |
|-------|-----------|------------------|-----------------|
| **Zhang et al., "Defect Tolerance in Homogeneous Manycore Processors Using Core-Level Redundancy with Unified Topology"** | DATE 2008 | Core-level redundancy (N+M spares) with reconfiguration to maintain unified mesh topology | **Closest to our work.** But: (a) assumes fixed spare positions, (b) small scale evaluation, (c) no workload awareness, (d) no diagonal link utilization |
| **Zhang et al., "On Topology Reconfiguration for Defect-Tolerant NoC-Based Manycore Systems"** | IEEE TVLSI 2009 | RRCS-gSA algorithm; proved topology reconfiguration is NP-complete | **Key reference.** Formalizes the problem. But: uses simulated annealing at small scale, no workflow-aware cost model |
| **Zhang et al., "Performance-Asymmetry-Aware Topology Virtualization"** | DATE 2010 | Accounts for performance asymmetry from different physical placements | Extends 2009 work with process variation awareness; still small scale, no deadlock-free routing analysis |
| Ke et al., "Hungarian Algorithm Based Virtualization for Defect-Tolerant NoC" | ASP-DAC 2012 | Hungarian algorithm for timing-similarity-based virtual topology mapping | Elegant optimization; but: global assignment (not scalable to 1000s of nodes), no routing guarantee |
| Ding et al., "Two-Stage Degradation-Based Topology Reconfiguration" | ACM TACO 2025 | Greedy bidirectional column reconfiguration; proved maximality | Latest work in this line; focuses on maximizing fault-free array, not workload-aware |
| Qian et al., "Efficient Topology Reconfiguration: Greedy-Memetic Algorithm" | J. Parallel Dist. Computing 2024 | Two-level greedy + memetic algorithm for topology reconfiguration | Improved scalability over SA; still no workflow awareness or deadlock analysis |

### Key Differences from Our Work:
1. **Scale:** Prior works evaluated on <128 cores; ours scales to 512x512
2. **Workload awareness:** Prior works optimize topology-only metrics (hop count); ours uses workflow-aware cost model (GEMM/GEMV communication patterns)
3. **Routing guarantee:** Prior works assume dimension-order routing still works after reconfiguration; ours provides explicit deadlock-free routing via submesh hierarchy
4. **Link diversity:** Prior works only consider same-topology remapping; ours handles mesh-to-diagonal-mesh (utilizing extra routing resources)

---

## Category 4: Deadlock-Free Routing on Irregular/Faulty Topologies

| Paper | Venue/Year | Key Contribution | Relevance / Gap |
|-------|-----------|------------------|-----------------|
| Dally & Seitz, "Deadlock-Free Message Routing in Multiprocessor Interconnection Networks" | IEEE TC 1987 | Channel dependency graph (CDG) formalism for deadlock freedom | Foundational theory our routing builds on |
| Glass & Ni, "The Turn Model for Adaptive Routing" | JACM 1994 | Prohibiting 1/4 of turns prevents deadlock without VCs | Foundational; assumes regular mesh |
| Duato, "A New Theory of Deadlock-Free Adaptive Routing" | IEEE TPDS 1993/1995 | Escape sub-network guarantees deadlock freedom | Theoretical basis for our hierarchical routing |
| Koibuchi et al., "Fault-Tolerant Deadlock-Free Routing Based on Odd-Even Turn Model" | IEEE TC 2003 | Extended odd-even model to tolerate unbounded faults in rectangular blocks | Requires faults in rectangular blocks; our faults are arbitrary |
| Holsmark et al., "Deadlock-Free Routing for Irregular Mesh NoC with Rectangular Regions" | J. Systems Architecture 2008 | VC-based and turn-prohibition routing for irregular mesh NoC | Handles regions but not arbitrary per-node faults |
| Ebrahimi et al., "Reconfigurable Routing (FDOR) for Fault-Tolerant 2D-Mesh NoC" | ~2010 | Flexible DOR adapts to topology changes while maintaining deadlock freedom | Runtime reconfigurable; complementary to our approach |
| **Fick et al., "Vicis: Highly Resilient Routing for Fault-Tolerant NoCs"** | DATE 2009 | Two-level fault tolerance (intra-router + inter-router rerouting); handles 50% router failures | Impressive resilience but: router-level, not topology remapping; no workload awareness |
| **ARIADNE (Catania et al.)** | PACT 2011 | Topology-agnostic reconfiguration using up*/down* routing for deadlock freedom | **Key comparison.** Handles arbitrary faults; but: up*/down* limits path diversity, no workload awareness |
| **uDIREC (Aisopos et al.)** | MICRO 2013 | Unified diagnosis + reconfiguration with MOUNT routing; uses all functional links | **Published at MICRO.** Most comprehensive prior work on fault-tolerant deadlock-free routing; but: no virtual topology abstraction, no workload-specific optimization |
| Skeie et al., "Flexible DOR for Virtualization of Multicore Chips" | SoC 2009 | Extended DOR for irregular 2D/3D mesh from virtualization | Connects virtualization to routing; limited fault model |
| Sun et al., "Convex-Based DOR for Virtualization of NoC" | NPC 2010 | CBDOR for convex virtual topologies; 2.2% area overhead | Restricted to convex shapes |

**Gap:** Prior deadlock-free routing works either (a) assume specific fault patterns (rectangular blocks), (b) don't combine with virtual topology remapping, or (c) don't optimize for specific workloads.

---

## Category 5: Wafer-Scale / Cerebras Defect Tolerance

| Paper | Venue/Year | Key Contribution | Relevance / Gap |
|-------|-----------|------------------|-----------------|
| Sean Lie, "Wafer-Scale Deep Learning" | Hot Chips 2019 | WSE-1: 400K cores, ~1% spare cores, redundant fabric links | Our target platform class; uses hardware redundancy only |
| Sean Lie, "Inside the Cerebras Wafer-Scale Cluster" | IEEE Micro 2024 | WSE-2 cluster: SwarmX fabric, distributed autonomous repair | Confirms regular mesh exposed despite diagonal links; motivates our diagonal link utilization |
| Cerebras, "100x Defect Tolerance" | Blog 2025 | Cores shrunk to 0.05mm^2; fabric routes around defects | Hardware-only solution; doesn't optimize for workload |
| "Wafer-Scale AI Compute: A System Software Perspective" | ACM SIGOPS 2025 | Describes Cerebras WSE driver performing hardware remapping to bypass defective cores/links and preserve virtual 2D mesh | **Important:** Confirms Cerebras does software-level remapping, but only to restore regular mesh (not to optimize for workload or exploit extra links) |

**Gap:** Cerebras uses hardware redundancy + regular topology exposure. Their SIGOPS 2025 paper confirms software remapping exists but only restores regularity. Our work goes further: remapping to optimize for specific workloads AND utilizing extra routing resources (diagonal links).

---

## Category 6a: Deadlock-Free Mapping for Neural Network / Accelerator Chips

| Paper | Venue/Year | Key Contribution | Relevance / Gap |
|-------|-----------|------------------|-----------------|
| "A Deadlock-Free Physical Mapping Method on the Many-Core Neural Network Chip" | Neurocomputing 2020 | SA-based mapping with two deadlock-free constraints for neural network chips; saves 30-41% routing time | **Relevant:** Combines deadlock-free + workload-aware + physical mapping. But: SA-based (not scalable to 512x512), single chip topology, no defect tolerance |
| Xue et al., "System Virtualization for Neural Processing Units" | HotOS 2023 | Position paper on NPU virtualization challenges including topology partitioning | Early vision; no concrete implementation |
| Lischka & Karl, "Virtual Network Mapping via Subgraph Isomorphism" | ACM VISA (SIGCOMM) 2009 | Maps virtual networks via subgraph isomorphism simultaneously for nodes and links | Algorithmic reference; cloud-scale, not chip-scale |
| Clark et al., "Scalable Subgraph Mapping for Acyclic Computation Accelerators" | CASES 2006 | Subgraph isomorphism for mapping computation onto hardware accelerators | Different target (acyclic computation graphs), but related technique |
| TGE: "ML-Based Task Graph Embedding for Large-Scale Topology Mapping" | IEEE IPDPS 2017 | Graph embedding + ML for topology-aware mapping in HPC | Interesting approach; HPC-scale but not defect-aware |

---

## Category 6: Chiplet / NoC Topology Papers (from Prep Guide)

| Paper | Venue/Year | Key Contribution |
|-------|-----------|------------------|
| Yin et al., "Modular Routing for Chiplet-Based Systems" | ISCA 2023 | Topology-agnostic, deadlock-free routing for chiplets |
| Zheng et al., "NN-Baton" | ISCA 2021 | Workload-to-chiplet mapping optimization |
| Kannan et al., "Kite" | DAC 2020 | Heterogeneous interposer topologies |
| Feng et al., "vNPU" | ISCA 2025 | Virtual topology creation + best-effort topology mapping for NPUs |
| Xue et al., "NPU Virtualization" | MICRO 2024 | Hardware-assisted NPU virtualization for cloud |

---

## Positioning Our Work

### What exists:
- VNE: cloud-scale, revenue-driven, no hardware defects (Category 1)
- Task mapping: per-application, small scale, no topology remapping (Category 2)
- Topology reconfiguration: closest, but small scale, no workload/routing co-optimization (Category 3)
- Deadlock-free routing: handles faults but not combined with topology virtualization (Category 4)
- Cerebras: hardware-only redundancy (Category 5)

### What we uniquely provide:
1. **Scale:** Hierarchical remapping algorithm (KdTree + submesh partitioning) that scales to 512x512+ meshes — orders of magnitude beyond prior topology reconfiguration works
2. **Workload awareness:** Cost model incorporates GEMM/GEMV communication patterns, not just hop-count minimization
3. **Integrated deadlock-free routing:** Submesh hierarchy routing with ascend-then-descend guarantee — not a separate post-hoc fix
4. **Link diversity exploitation:** Mesh-to-diagonal-mesh remapping utilizes routing resources that Cerebras-style systems leave unused
5. **Comprehensive fault model:** Handles arbitrary faults across PUs, routers, AND links simultaneously

### Strongest comparisons for the paper:
- **Zhang et al. (TVLSI 2009)** — Same problem, different scale and approach
- **uDIREC (MICRO 2013)** — Same venue, deadlock-free on faults, but no topology virtualization
- **ARIADNE (PACT 2011)** — Topology-agnostic reconfiguration, but up*/down* limits performance
- **vNPU (ISCA 2025)** — NPU topology virtualization, closest in spirit but different target (NPU cores, not general mesh)
- **Cerebras (Hot Chips 2019 / IEEE Micro 2024)** — Motivating platform, hardware-only baseline
