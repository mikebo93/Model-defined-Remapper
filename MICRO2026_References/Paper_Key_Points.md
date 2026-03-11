# Paper Key Points & Contribution Notes

## Problem Statement

### 1. Regularity Requirement
- Most kernels and algorithms (GEMM, GEMV, convolution, etc.) require regular hardware topology due to:
  - **Structural regularity:** uniform neighbor counts enable systolic/dataflow patterns
  - **Latency predictability:** dimension-order routing on regular meshes gives deterministic hop counts
  - **Programming simplicity:** applications assume a clean coordinate space

### 2. Defect Reality in Hardware
Real hardware inevitably has defects. Current mitigation approaches:

#### (2i) Hardware Redundancy
- Chip designed with spare cores, routers, and links
- Defective components swapped with redundant ones, exposing regular topology to users
- **Examples:**
  - AMD MI300 series: redundant XCDs (chiplet-level redundancy)
  - Cerebras CS-2/CS-3: WSE has redundant cores and routers across 850,000+ cores
- **Key observation for Cerebras:** Even with redundant diagonal links in the physical fabric, only regular 2D mesh is exposed to users — **wasting routing resources**

#### (2ii) Software Discard
- Discard defective area entirely
- Find largest defect-free regular sub-topology and use only that
- Simpler but wasteful

### 3. The Utilization Problem (Our Motivation)
Both approaches cause hardware underutilization:
- **(3i) Area discard:** Usable-but-irregular regions are abandoned for topological regularity. At higher defect rates, this waste is substantial.
- **(3ii) Redundancy overhead:** Spare cores/routers consume die area and power. Redundancy is fixed at design time (may be insufficient or excessive). Extra routing resources (e.g., diagonal links) go unused when only regular topology is exposed.

### 4. Our Proposal: Model-Defined Remapper
We propose decoupling the virtual topology (seen by software) from the physical topology (actual hardware):
- A **model-defined remapper** transparently maps a virtual regular mesh onto ALL available healthy nodes in a faulty physical mesh
- Applications still see a regular topology (programming model unchanged)
- Maximizes hardware utilization by using defective areas (routing around faults)
- **Defect-tolerant** — works with arbitrary fault patterns

---

## Why Not Other Topologies?

### Clos Networks
- Easier to handle defects: just replace defective switch with a healthy spare at the same stage
- Symmetric, multi-path redundancy makes fault tolerance simpler
- **BUT:** Not all designs can use Clos:
  - 2D topologies are far more manufacturing-friendly for monolithic chips and interposers
  - Clos requires multi-stage switching which doesn't map well to 2D silicon layout
  - Large-scale chips (Cerebras WSE) and chiplet systems naturally use 2D mesh/torus

### Fully-Connected (All-to-All)
- Trivial for routing (1 hop to anywhere)
- Works for small core counts (e.g., AMD MI300 with ~8 XCDs)
- **BUT:** Not scalable:
  - O(N^2) links — unaffordable for large-scale chips (hundreds/thousands of cores)
  - Wire length and area grow quadratically
  - Not relevant for the scale where defect tolerance matters most

### Our Target: Large-Scale 2D Topologies
- **Why 2D mesh is dominant for large chips:**
  - Manufacturing-friendly (planar layout)
  - Scalable (O(N) links)
  - Matches physical silicon/interposer substrate
- **Where our work has most impact:**
  - Asymmetric and large-scale topologies (Cerebras-class)
  - Chiplet interposers with 2D NoC
  - Systems where defect rates make redundancy alone insufficient

---

## Key Contributions

### Contribution 1: Virtual-to-Physical Topology Remapping Framework
- Formal decoupling of virtual and physical topology
- The underlying graph embedding problem is **NP-hard** (generalizes subgraph isomorphism with cost minimization), so exact solutions are intractable at scale
- Hierarchical spatial search heuristic (KdTree + submesh partitioning) for scalable, near-optimal mapping
- Workflow-aware cost model that optimizes for actual communication patterns

### Contribution 2: Deadlock-Free Routing on Irregular Topologies
- Submesh hierarchy routing with ascend-then-descend constraint
- Guarantees deadlock-freedom even on arbitrarily defective physical meshes
- Works for both 4-connected (standard mesh) and 8-connected (diagonal mesh) topologies
- **This is non-trivial:** naive routing on irregular/remapped topologies easily introduces deadlocks

### Contribution 3: Utilizing "Wasted" Routing Resources
- Demonstrated with mesh-to-diagonal-mesh mapping:
  - Physical chip has diagonal links (like Cerebras) but only exposes regular 2D mesh
  - Remapper can leverage these diagonal links for shorter physical paths
  - Reduces hop count and congestion after remapping

### Contribution 4: Evaluation on Realistic Scenarios
- Tested across multiple topology sizes (up to 512x512)
- Multiple fault rates (PU: 7%, Router: 3.5%, Channel: 0.7%)
- Multiple workloads (GEMM, GEMV)
- Comparison: healthy baseline vs. defective with remapping
- Metrics: latency, throughput, mapping quality (node cost, path cost)

---

## Experiment Coverage

| Experiment | Virtual Topology | Physical Topology | Purpose |
|------------|-----------------|-------------------|---------|
| MeshScaling | 2D Mesh (various sizes) | 2D Mesh (1.5x, faults) | Scalability analysis |
| RemappedExperiment | 2D Mesh (256, 512) | 2D Mesh (1.5x, faults) | Main defect tolerance eval |
| Diagonal mapping | 2D Mesh | 8-connected Diagonal Mesh (faults) | Unused routing resource utilization |

---

## Open Questions / Future Work
- How does mapping quality degrade with defect rate?
- Can the remapper handle non-mesh virtual topologies (torus, hypercube)?
- Runtime remapping (online fault discovery)?
- Integration with real hardware (Cerebras SDK, chiplet platforms)?
