# Paper Notes

## 1. Zhang et al. 2008 — "Defect Tolerance in Homogeneous Manycore Processors Using Core-Level Redundancy with Unified Topology"

- **Authors:** Lei Zhang, Yinhe Han, Qiang Xu, Xiaowei Li
- **Venue:** DATE '08, March 2008
- **DOI:** https://doi.org/10.1145/1403375.1403591
- **Detailed notes:** `reference/Zhang2008_Defect_Tolerance_Unified_Topology.md`

### What they do
- AMAD scheme: remap healthy cores into a "logical topology" isomorphic to a reference mesh
- RRCS algorithm (Row Ripping + Column Stealing) → Simulated Annealing refinement
- Metrics: Distance Factor (DF) + Congestion Factor (CF)

### Limitations (vs. our work)
1. **No workload awareness** — uses generic traffic patterns; doesn't consider application-specific dataflows (GEMM, GEMV)
2. **No geometric/spatial fidelity** — only hop distance and link congestion; no angular distortion or spatial coherence metrics (what our RANSAC check addresses)
3. **Scalability** — tested up to 8×8 only; flat SA with no hierarchical structure; visible topology skew at higher fault rates
4. **Core faults only** — does not model router or channel faults
5. **No deadlock-freedom guarantee** — routing not explicitly addressed
6. **No diagonal link utilization** — 4-connected mesh only; unused spare resources hidden

---

## 2. Pan et al. 2025 — "Stratum: System-Hardware Co-Design with Tiered Monolithic 3D-Stackable DRAM for Efficient MoE Serving"

- **Authors:** Yue Pan, Zihan Xia, Po-Kai Hsu, Lanxiang Hu, Hyungyo Kim, Janak Sharda, Minxuan Zhou, Nam Sung Kim, Shimeng Yu, Tajana Rosing, Mingu Kang
- **Venue:** MICRO '25 (58th IEEE/ACM International Symposium on Microarchitecture), October 2025, Seoul
- **DOI:** https://doi.org/10.1145/3725843.3756043

### What they do
- System-hardware co-design for serving MoE (Mixture-of-Experts) LLMs using Monolithic 3D-Stackable DRAM (Mono3D DRAM) instead of HBM
- Mono3D DRAM: DRAM layers fabricated sequentially on the same wafer with Cu-Cu hybrid bonding (~1μm pitch, 5× finer than HBM TSVs), achieving 19–30 TB/s internal bandwidth
- **In-memory tiering:** 1024 WL layers divided into 8 tiers with heterogeneous access latency (1.11ns top → 22.88ns bottom); hot experts placed on fast tiers, cold experts on slow tiers
- **NMP processor:** 16 PUs on logic die (7nm), hybrid-bonded to DRAM; each PU has 16 near-bank PEs with tensor cores, ring router, shared memory
- **Topic-based expert placement:** DistilBERT classifier tags queries by topic → scheduler batches same-topic queries → maps frequently-activated experts to fast DRAM tiers
- **Results:** up to 8.29× decoding throughput and 7.66× energy efficiency vs GPU baselines

### What we can learn (presentation & methodology, not topic)

#### L1. Cross-layer evaluation structure
Stratum evaluates at **four levels**: device (Mono3D DRAM circuit simulation via NeuroSim + Coventor TCAD), circuit (logic die synthesized in 7nm ASAP7), algorithm (topic classifier accuracy, expert placement hit rates), and system (end-to-end throughput/energy vs GPU baselines). This multi-level evaluation convinced reviewers that every piece of the system works.

**Takeaway for us:** We should also evaluate at multiple levels:
- **Algorithm level:** mapping quality (node cost, path cost), scalability (mapping time vs mesh size)
- **Architecture level:** deadlock freedom proof/verification (CDG acyclicity), routing overhead (path stretch)
- **Workload level:** GEMM/GEMV latency and throughput, congestion breakdown
- **Comparison level:** vs healthy baseline, vs discard baseline, vs prior art (Zhang et al.)

#### L2. Quantitative baselines with real systems
Stratum compares against concrete GPU baselines (RTX A6000, H100 with vLLM) — not just prior academic work. This grounds the results in what practitioners actually use.

**Takeaway for us:** If possible, compare our remapper against what Cerebras actually does (discard faulty area, expose regular sub-mesh). Even an estimated baseline from public Cerebras specs would strengthen the paper.

#### L3. Sensitivity analysis across multiple dimensions
Stratum varies batch size, Mono3D DRAM layer count, sequence length, and hot expert hit rate — each revealing a different insight about when and why the system wins.

**Takeaway for us:** Our sensitivity analysis should vary:
- Fault rate (the primary knob)
- Physical-to-virtual area ratio
- Mesh scale
- Workload type (GEMM vs GEMV)
Each reveals different aspects: fault rate shows robustness, area ratio shows the redundancy trade-off, scale shows algorithmic scalability, workload shows application specificity.

#### L4. Concrete hardware feasibility analysis
Stratum includes area breakdown (76.63 mm² logic die, 63% utilization within 121 mm² budget), power breakdown (144.53W total), and thermal analysis. This convinces reviewers the design is buildable.

**Takeaway for us:** We should include a concrete cost analysis of the remapper itself — e.g., mapping time in seconds/minutes, memory footprint of the mapper, and how these scale. This is our equivalent of "feasibility" — showing the remapper is practical to run at manufacturing/boot time.

#### L5. Problem decomposition narrative
Stratum clearly separates **what** needs to happen (serve MoE efficiently) from **why** existing approaches fail (HBM bandwidth wall, heterogeneous DRAM latency) from **how** they solve it (tiering + NMP + topic-based placement). Each challenge maps cleanly to a design component.

**Takeaway for us:** Our Challenges section (§3) should have a 1:1 mapping to Design components (§4):
- Scalability challenge → Hierarchical spatial search (§4.2)
- Application specificity challenge → Workload-aware cost function (§4.3)
- Routing correctness challenge → Submesh hierarchy routing (§4.5)

This makes the paper feel inevitable — each design decision is motivated by a specific, named challenge.

#### L6. Overhead analysis
Stratum explicitly measures overhead of their optimizations: topic classifier adds <2% latency, expert swaps cost <1% time and energy. This preempts reviewer concerns.

**Takeaway for us:** We should explicitly report:
- Mapping time overhead (one-time cost at boot/manufacturing)
- Routing table size overhead (memory per node)
- Path stretch from submesh hierarchy routing vs shortest path
- Any throughput loss from non-ideal mapping vs healthy baseline

---

## 3. Luczynski, Gianinazzi et al. 2024 — "Near-Optimal Wafer-Scale Reduce"

- **Authors:** Piotr Luczynski, Lukas Gianinazzi, Patrick Iff, Leighton Wilson (Cerebras), Daniele De Sensi, Torsten Hoefler
- **Venue:** HPDC 2024 (arXiv:2404.15888v3)
- **Note:** Leighton Wilson is from Cerebras Systems — this paper has insider knowledge of WSE architecture.

### What they do
- First systematic study of Reduce and AllReduce collectives on the Cerebras WSE (CS-2)
- Develop a performance model that predicts runtime with <4% error
- Design new algorithms (Two-Phase, Auto-Gen) that outperform Cerebras vendor implementations by up to 3.32× (Reduce) and 2.56× (AllReduce)
- Establish lower bounds for 1D Reduce runtime
- Validate on actual CS-2 hardware (750K PEs, 850 MHz)

### WSE architecture details (useful reference)
- Each PE: 48KB SRAM, router with 5 bidirectional links (4 neighbors + 1 ramp to processor)
- **Link bandwidth: 32 bits/cycle per direction** (data sent as 32-bit "wavelets")
- **1 cycle** to traverse a link; T_R ≈ 2 cycles ramp latency between router and processor
- **Routers support multicast** — can duplicate a wavelet to multiple directions at no extra cost
- **Color-based routing:** each wavelet has a color; router stores up to 4 routing configurations per color, allowing runtime reconfiguration
- **Dataflow architecture:** tasks activated by arriving wavelets, not explicit scheduling
- **Defect handling (p.9):** "If there are any defects, a proprietary process will route around them" — confirms Cerebras does remapping but never discloses the algorithm
- **Single-wavelet routing** (not wormhole) — each wavelet is an independent 32-bit packet, unlike our multi-flit wormhole messages

### The Spatial Computer Model

The **spatial computer model** is a performance modeling framework for distributed architectures where computation is spatially distributed across a physical substrate (as opposed to traditional models that assume a central processor with hierarchical memory). The key idea: on a spatial computer, **communication cost is determined by physical distance**, not just message count.

The model originated from work on analyzing algorithms for spatially distributed systems (cited as [17] in the paper). It decomposes application performance into 4 independent cost dimensions:

| Term | Name | Meaning |
|------|------|---------|
| **E** | **Energy** | Total number of hops across ALL messages in the entire computation. Represents total network load. If the network has N links, E/N gives a **lower bound** on runtime assuming perfect load balancing — you can't finish faster than this even if traffic were spread perfectly evenly across all links. In practice, traffic concentrates on specific paths, so actual runtime can be much worse than E/N. |
| **L** | **Distance** | The longest path any single message must travel (hops). A hard latency floor — no message can arrive faster than L cycles regardless of network load. |
| **D** | **Depth** | The longest sequential chain of dependent operations. If operation B depends on the result of operation A, they cannot overlap. D counts the longest such chain. For Cannon's algorithm, D = M (number of shift steps). |
| **C** | **Contention** | The maximum number of messages any single PE must receive. A PE receiving C messages needs at least C cycles to process them (one at a time). This is the ejection bottleneck. |

These combine into a **lower bound** on runtime:
```
T ≥ max(C, E/N + L) + (2T_R + 1)·D
```

The max() means: runtime is at least as long as whichever bottleneck dominates (contention OR network throughput + latency), plus the sequential depth overhead.

**Why it's a lower bound, not an estimate:**
- `E/N` assumes all links share load uniformly — in reality, some links are hot (heavily used) and others idle. A single overloaded path serializes its traffic regardless of how idle other links are.
- `max(C, E/N + L)` assumes contention and network delay fully overlap — in reality, a PE both waits for messages to arrive (network delay) AND processes them sequentially (contention). These costs can stack (`+`), not just overlap (`max`).
- The paper's goal is algorithm design (find the best collective pattern), so lower bounds are the right tool. For comparing actual runtimes of different mappings (our goal), an estimate with `+` is more appropriate.

### What we can learn

#### L1. Our additive model is correct for our purpose
Their max() structure gives lower bounds for algorithm design. Our additive model (`t_routing + t_link_queuing + t_ejection_queuing`) gives runtime estimates for comparing mappings. Different goals → different model structures. We don't need to adopt max().

#### L2. Energy term as a sanity check
While E/N is just a lower bound, it's a useful **sanity check** for our remapper: compute total energy E = Σ(traffic × physical_hops) for a mapping. If E/N already exceeds computation time, the mapping is guaranteed to be network-bound — no amount of routing optimization will help, and we should try a different mapping. This is cheap to compute from the mapping without simulation.

#### L3. Precise contention definition
They define C = max packets any PE receives per step. We should similarly define our ejection queuing precisely rather than leaving it as a vague term. For Cannon on a healthy mesh: C = 2 per step (one A-shift horizontal, one B-shift vertical). After remapping: C can increase if multiple physical paths converge at one node.

#### L4. Validation methodology
They validate their model against actual hardware measurements with <4% error. We should similarly validate our analytical model against our simulator — report prediction error across scales and fault rates to show the model is trustworthy.

#### L5. Cerebras defect confirmation
Page 9 confirms: "If there are any defects, a proprietary process will route around them." This is a useful citation confirming Cerebras does remapping but the algorithm is undisclosed — supporting our claim that defect-tolerant remapping is an important but unsolved (in the open literature) problem.

---

## 4. Industry Defect Handling: Spare Cores and Yield Binning

### Two strategies in practice

**Strategy 1 — Discard/bin (GPUs, CPUs):** Over-provision the die, fuse off defective units, sell as lower SKU.
- NVIDIA: GA102 has 84 SMs → RTX 3090 uses 82, RTX 3080 uses 68. AD102 has 144 SMs → RTX 4090 uses 128. GH100 has 144 SMs → H100 SXM uses 132, H100 PCIe uses 114.
- AMD: Navi 31 has 96 CUs → 7900 XTX uses 96 (full), 7900 XT uses 84 (harvested). Zen 3 CCD has 8 cores → Ryzen 5 5600X uses 6.
- Intel: Sapphire Rapids tile has ~15 cores → Xeon uses 14 (1 yield guard).
- **Why this works:** GPU SMs and CPU cores are independent or crossbar-connected. Disabling an SM doesn't break any topology — there's no mesh to create a hole in.

**Strategy 2 — Spare cores + remap (mesh-connected accelerators):**
- Cerebras WSE-1: ~406K cores, ~1.5% spare. WSE-3: ~900K cores. Routes around defects via undisclosed algorithm.
- Tesla Dojo D1: 360 core sites, 354 enabled, 6 spare (1.7%).
- **Why VCs/remap needed:** Cores are mesh-connected. Disabling a core creates a hole → irregular topology → need routing reconfiguration → need VCs for deadlock freedom.

### Key insight for the paper
Discard/bin works when compute units are independent (GPU SMs via crossbar, CPU cores via ring/crossbar). It **fails** for mesh-connected architectures because a disabled interior node creates an irregular topology that breaks dimension-order routing. This is the fundamental reason mesh-connected architectures (Cerebras, Dojo, chiplet interposers) need topology remapping — and why remapping needs VCs.

### Sources
- NVIDIA GA102 Whitepaper (Ampere architecture)
- NVIDIA Hopper Architecture In-Depth (developer.nvidia.com)
- Tom's Hardware: AMD RX 7900 XTX/XT review
- AnandTech: AMD Zen 3 Ryzen Deep Dive
- Cerebras blog: "100x Defect Tolerance"
- Chips and Cheese: "Hot Chips 34: Tesla's Dojo Microarchitecture"

---

## 5. Virtual Channels in Modern Hardware (Justification for ≥2 VC Assumption)

Our deadlock-free submesh hierarchy routing requires ≥2 VCs. This is conservative — every modern mesh/torus architecture provides far more.

**Detailed reference:** `reference/Virtual_Channels_in_Modern_Hardware.md`

### Key products (TRUE virtual channels only — general-purpose, reassignable):
| Platform | VCs | Mechanism |
|----------|-----|-----------|
| Cerebras WSE-2/3 | **24** colors | Any color carries any data; time-multiplexed, non-blocking |
| Google TPU v4+ (ICI) | **≥2** | Torus dateline routing |
| Cray T3D/T3E | **2** | Dateline VC for torus |
| IBM Blue Gene/L | **2** | Deterministic + adaptive |

Note: Intel Skylake-SP (AD/AK/BL/IV) and ARM CHI (REQ/RSP/SNP/DAT) are **protocol-level virtual networks** — each dedicated to a specific message class, NOT reassignable by routing algorithms. These do not count as true VCs for our argument.

### Key academic reference:
- Li et al., "Determining the Minimum Number of Virtual Networks for Different Coherence Protocols," **ISCA 2024**. Proves that all practical coherence protocols require ≥2 virtual networks. https://ieeexplore.ieee.org/document/10609584/

### AMD and NVIDIA — inconclusive
- **AMD Infinity Fabric:** Proprietary architecture; no public documentation of VC counts. Likely ≥2 VCs (uses torus-like topologies in multi-socket which require VCs for deadlock avoidance), but cannot be confirmed.
- **NVIDIA GPU NoC:** Uses **crossbar** internally (single-stage, fully-connected switch), not a mesh with routers. No multi-hop routing → VCs not applicable. NVLink/NVSwitch is also crossbar-based. Cannot use as evidence for mesh VC counts.

### Adversary case: commercial products WITHOUT VCs

**Single-die products (mesh doesn't cross die boundaries):**
- **Tilera TILE-Gx72:** Single die (40nm), 8×9 on-chip mesh, 5 physical networks, XY routing. Yield binning to lower SKUs (72→36→16→9) by fusing off edge cores. Interior router defect → discard die. Source: Wikipedia "TILE-Gx"; Semiaccurate 2013.
- **Kalray MPPA-256 (Bostan):** Single die (28nm), 2D **torus** (not mesh) at cluster granularity, explicitly "wormhole switching without virtual channels," turn-model routing. Faulty core in cluster → no NoC impact; faulty cluster router → discard die. Source: De Dinechin et al., DAC 2017.

**Multi-chip products:**
- **Adapteva Epiphany:** Single die per chip, BUT eMesh **explicitly designed for multi-chip extension** — 4 LVDS links per chip, up to 64 chips in seamless 2D mesh with flat global addressing. 3 physical networks, XY routing, no VCs. **No documented defect-tolerance for multi-chip topology** — a dead chip in the middle breaks XY routing and this was never addressed. Source: Epiphany Architecture Reference; Olofsson, arXiv:1610.01832, 2016.
- **SpiNNaker:** 57,600 chips in triangular torus (6 links/chip), no VCs. Handles dead chips via **packet dropping + emergency rerouting** (lossy). Source: Navaridas et al., Parallel Computing, 2015; Furber et al., IEEE TC, 2013.

**Conclusion:** Single-die VC-free products discard the die on interior defects. The one VC-free product with a multi-chip extensible mesh (Adapteva) **never solved** the hole-in-mesh problem. SpiNNaker tolerates loss. The only products that handle interior defects in multi-die meshes losslessly — Cerebras (24 VCs), Google TPU (≥2 VCs) — all use virtual channels. Our ≥2 VC requirement is the inherent cost of choosing utilization over waste.

---

## 6. Yoo, Won et al. 2025 — "Toward a Standardized Representation for Deep Learning Collective Algorithms"

- **Authors:** Jinsun Yoo, William Won, Meghan Cowan, Nan Jiang, Benjamin Klenk, Srinivas Sridharan, Tushar Krishna
- **Venue:** IEEE Micro, Vol. 45 No. 2, March/April 2025 (Hot Interconnects 31)
- **DOI:** https://doi.org/10.1109/MM.2025.3547363

### What they do
- Propose using **Chakra Execution Trace (ET)** as a common representation for both distributed ML workloads and collective algorithms
- Extend Chakra ET to encode arbitrary collective algorithms by decomposing them into three primitive node types:
  - **COMM_SEND:** point-to-point message send to a destination NPU
  - **COMM_RECV:** wait for a point-to-point message from a source NPU
  - **COMP:** run a compute task (e.g., reduction)
- This **decouples the algorithm implementation from the collective's name** — an "All-Reduce" is not a black box but a specific DAG of sends, receives, and reductions
- Show proof-of-concept: MSCCLang DSL and TACOS synthesizer both produce Chakra ET, consumed by ASTRA-sim simulator
- Key benefit: enables co-optimization of compute and communication (Figure 4 — fine-grained overlap of All-Gather chunks with matrix multiplication)

### Key technical details
- Each Chakra ET trace = multiple DAGs (one per NPU), vertices = operations, edges = dependencies
- Collective algorithms represented as per-NPU task graphs of COMM_SEND/COMM_RECV/COMP nodes
- Ring-based Reduce-Scatter example: each NPU repeatedly sends to next, receives from previous, then reduces — represented as sequential [SEND → RECV → COMP] chains
- Topology-aware algorithms (TACOS) produce more complex DAGs with parallel dependencies
- Common representation enables plug-and-play: swap algorithm Chakra ET files without modifying downstream tools

### Relevance to our work — used in §4.2
Our IR decomposes operators into the same three primitive task types (SendTask, ReceiveTask, ProcessTask) organized as per-core DAGs. We cite this paper to establish that decomposing named operations into send/receive/compute primitives is a recognized approach:

| Chakra ET | Our IR | Scope |
|-----------|--------|-------|
| COMM_SEND | SendTask (message_id, message_size) | Per-message |
| COMM_RECV | ReceiveTask (message_id) | Per-message, paired with send |
| COMP | ProcessTask (process_id, steps) | With explicit duration |
| DAG per NPU | TaskGraph per actor | Per-core dependency tracking |

**Key difference in scope:** They decompose *communication collectives* (All-Reduce → sends/receives across distributed NPUs). We decompose *compute operators* (GEMM → data distribution + local compute + reduction across mesh cores). Our decomposition is at a finer granularity and on a spatial architecture.

**Additional advantage of our IR:** Two-level hierarchy (Work → Task). Works provide semantic-level patterns (Unicast, Reduce, Gather, AllToAll) that decompose into executable Tasks. Chakra ET is flat — just nodes in a DAG. Our Work-level gives composability that Chakra ET lacks.

---

### Citations to add to references.bib (not all PDFs downloadable):
- Cerebras SDK docs: https://sdk.cerebras.net/computing-with-cerebras (web reference)
- Intel mesh: WikiChip https://en.wikichip.org/wiki/intel/mesh_interconnect_architecture (web reference)
- Miles Dai, "Reverse Engineering the Intel Cascade Lake Mesh Interconnect," MIT M.Eng. Thesis, 2021 (PDF not downloaded — behind MIT DSpace)
- ARM CHI spec: https://developer.arm.com/documentation/102407/latest/ (web reference, couldn't fetch actual content)
- Li et al. ISCA 2024: https://ieeexplore.ieee.org/document/10609584/ (behind IEEE paywall — download if institutional access available)
- Lopes et al., "Uncovering Real GPU NoC Characteristics," MICRO 2024 (behind ACM paywall — not downloaded)
- Chiu, "The Odd-Even Turn Model for Adaptive Routing," IEEE TPDS, 2000 (already cited via glass1994turn lineage)
