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
