## Remapper Project — Paper Background Outline

### 1. Defects Are Inevitable

Semiconductor defects follow a bathtub curve: high infant mortality, a stable useful-life period, then increasing wear-out failures. Critically, as devices age, defect rates rise — components that pass initial screening may still develop faults over their operational lifetime. Combined with shrinking process nodes and growing die/wafer areas, the probability of at least one defect per chip approaches certainty. Designers must plan for defects, not hope to avoid them.

- Reference: https://testflowinc.com/blog/semiconductor-defect-rate-bathtub-curve

### 2. Topology-Aware Computing Depends on Regularity

High-performance kernels (GEMM on systolic arrays, GEMV with broadcast+reduce, collective communications) are designed around **regular topologies** — they exploit predictable hop counts, uniform bandwidth, and symmetric routing to schedule data movement and balance load. A regular topology allows the compiler/runtime to reason about latency and throughput more effectively.

### 3. Redundancy: The Industry's Current Answer

To maintain regularity despite inevitable defects, chip designers provision **spare components** and remap defective units to healthy ones, exposing an ideal topology to software:

- **AMD MI250X/MI300X:** Each compute die has 2 extra Compute Units (CUs) disabled for yield (112→110 per GCD on MI250X, 40→38 per XCD on MI300X). Software sees a uniform CU count regardless of which units are harvested. (ref: `reference/AMD_MI_Series_Redundancy.md`)
- **Cerebras WSE-3:** 970K physical cores, 900K active (~7% spare). Defective cores are locally replaced; the 2D mesh fabric reroutes around them transparently. (ref: `reference/Cerebras_WSE_Redundancy.md`)

### 4. Symmetric vs. Asymmetric Topologies: A Tale of Two Recovery Stories

**Symmetric topologies (e.g., Clos networks):** Fault tolerance is straightforward. All middle-stage switches are functionally interchangeable — losing one reduces path diversity but not connectivity. The topology is acyclic, so conflicts cause congestion, never deadlock. Recovery is just graph recoloring (polynomial time). (ref: `reference/Clos_Network_Fault_Tolerance.md`)

**Asymmetric topologies (e.g., 2D mesh):** Every node is topologically unique. Removing a defective node creates an irregular "hole" that:
- Breaks routing assumptions (e.g., dimension-order routing may no longer work)
- Can introduce cyclic dependencies → **deadlock**
- Requires non-trivial remapping to restore a usable virtual topology

This fundamental difference between symmetric and asymmetric topologies means that defect tolerance for the latter remains an open and challenging problem — and is what this paper addresses.

### 5. The Hidden Cost of Redundancy: Wasted Resources

Current redundancy schemes hide unused spare components after remapping:
- **Spare routers and links** that are not on any active path are powered down or ignored.
- **Diagonal links** (e.g., in Cerebras WSE) exist in hardware but are not exposed in the virtual 2D mesh topology. These could provide extra routing bandwidth for memory-bound workloads.
- **Spare processing units** that survive defect replacement sit idle.

**Motivation:** Rather than hiding these resources, we want to **expose and utilize them** — turning redundancy overhead into a performance advantage.

### 6. Challenges of Defect-Aware Remapping

Exposing spare components creates an **irregular topology**, which raises several hard questions:

1. **NP-hardness:** Even isomorphic subgraph matching — the simplest form of topology mapping — is NP-complete [Karp 1972]. Approximate or relaxed mappings add further degrees of freedom but do not escape the fundamental combinatorial complexity. (ref: `reference/Subgraph_Isomorphism_NP_Hard.md`)
2. **Quality evaluation:** How do we measure whether a given remapping is good? Metrics must capture communication cost, load balance, and workload-specific performance (e.g., systolic array efficiency).
3. **Deadlock freedom:** Rerouting around defective nodes, routers, and channels on an irregular topology can introduce cyclic dependencies in the routing. How can we guarantee deadlock-free routing under arbitrary defect patterns?




#### Unrefined section start ####


### 7. Related Works
1. Zhang et al. 2008 — "Defect Tolerance in Homogeneous Manycore Processors Using Core-Level Redundancy with Unified Topology"






#### Unrefined section end ####






### 8. Our Approach (Detailed in Later Sections)

To address these challenges, we propose a hierarchical remapping framework that is both efficient and scalable:
- **Hierarchical search:** RCB partitioning + KdTree super nodes + parallel candidate evaluation — enabling remapping of meshes up to 512×512 in reasonable time.
- **Deadlock-free routing:** Submesh hierarchy routing (ascend-then-descend, no re-ascent) guarantees deadlock freedom on irregular, defect-induced topologies.



