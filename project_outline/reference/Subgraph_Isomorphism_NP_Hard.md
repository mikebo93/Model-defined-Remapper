# Subgraph Isomorphism / Virtual-to-Physical Mapping — NP-Hardness

## Summary

The subgraph isomorphism problem — given graphs H (pattern) and G (target), does G contain a subgraph isomorphic to H? — is **NP-complete** (Cook 1971, Karp 1972). The optimization/search version (finding the best embedding) is **NP-hard**. This directly applies to our remapping problem: embedding a virtual regular mesh (H) into a faulty physical mesh (G).

## NP-Completeness Proof Sketch

1. **In NP:** Given a candidate mapping, verify in polynomial time by checking edge preservation.
2. **NP-Hard (reduction from Clique):** Given instance (G, k) of the Clique Decision Problem (known NP-complete), construct subgraph isomorphism instance: "Is K_k a subgraph of G?" This is a special case of subgraph isomorphism, so subgraph isomorphism is at least as hard as Clique.

The problem remains NP-complete even for **planar graphs** (since Hamiltonian Cycle is NP-complete for planar graphs, and Hamiltonian Cycle reduces to subgraph isomorphism).

## Connection to Our Work

The virtual-to-physical topology remapping problem is a constrained subgraph isomorphism variant:
- **Pattern graph H:** Virtual regular 2D mesh (the workload topology)
- **Target graph G:** Physical mesh with defective nodes/links removed
- **Constraint:** Preserve adjacency (4-connected or 8-connected neighborhood)
- **Optimization:** Minimize communication cost / maximize locality

This is at least as hard as general subgraph isomorphism → **NP-hard** → justifies heuristic and hierarchical approaches (like our RCB partitioning + KdTree + parallel candidate evaluation).

## Virtual Network Embedding (VNE) — Same Problem in Networking

The VNE problem (mapping a virtual network onto a physical substrate) is explicitly formulated as a subgraph isomorphism variant and independently proven NP-hard. This provides additional citation support from the networking community.

---

## Sources & Where They Mention It

### 1. Subgraph Isomorphism Problem — Wikipedia
- https://en.wikipedia.org/wiki/Subgraph_isomorphism_problem
- Formal definition, NP-completeness classification.
- *"The subgraph isomorphism problem is NP-complete."* Cites Cook (1971) and Karp's 21 NP-complete problems (1972).
- Notes it generalizes Clique, Independent Set, and Hamiltonian Path.
- Remains NP-complete for planar graphs.

### 2. "Proof that Subgraph Isomorphism Problem is NP-Complete" — GeeksforGeeks
- https://www.geeksforgeeks.org/dsa/proof-that-subgraph-isomorphism-problem-is-np-complete/
- Step-by-step proof with Clique reduction.
- *"By reducing the Clique Decision Problem (which is NP-Complete) to the Subgraph Isomorphism Problem in polynomial time, every NP problem can be reduced to Subgraph Isomorphism in polynomial time, thereby proving it to be NP-Hard."*

### 3. "A Virtual Network Mapping Algorithm based on Subgraph Isomorphism Detection" (SIGCOMM VISA Workshop, 2009)
- https://conferences.sigcomm.org/sigcomm/2009/workshops/visa/papers/p81.pdf
- Explicitly connects VNE to subgraph isomorphism.
- Confirms NP-hardness of virtual-to-physical topology mapping.

### 4. "Virtual Network Embedding — An Optimization Problem" (Springer)
- https://link.springer.com/chapter/10.1007/978-3-642-30422-4_14
- NP-hardness of the optimization variant (minimizing resource usage).
- *"The VNE problem... is known to be NP-hard."*

### 5. "On the Complexity of the Virtual Network Embedding in Specific Tree Topologies" (arXiv, 2023)
- https://arxiv.org/abs/2311.05474
- Complexity analysis for restricted topology classes.
- Shows that even for specific tree structures, the problem can remain hard.

### 6. "Virtual Network Embedding through Topology Awareness and Optimization" (ResearchGate)
- https://www.researchgate.net/publication/257582253_Virtual_network_embedding_through_topology_awareness_and_optimization
- Heuristic approaches motivated by NP-hardness.

### 7. Original Complexity Theory References
- **Cook, S.A.** "The complexity of theorem-proving procedures." STOC 1971.
- **Karp, R.M.** "Reducibility among combinatorial problems." 1972. — Lists subgraph isomorphism among 21 NP-complete problems.

---

## Key Takeaway for Paper

The remapping problem (embedding a virtual mesh into a defective physical mesh) is a subgraph isomorphism variant and therefore NP-hard. This provides theoretical justification for our hierarchical heuristic approach (RCB partitioning + KdTree super nodes + parallel candidate evaluation) rather than exact search methods that would be intractable at scale (e.g., 512×512 meshes).
