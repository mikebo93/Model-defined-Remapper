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
