# Clos Network — Redundant Components for Defect Tolerance in Symmetric Topologies

## Summary

In a 3-stage Clos network C(m, n, r) with N = nr inputs/outputs, fault tolerance is achieved by adding **extra middle-stage switches** beyond the minimum needed for nonblocking operation. If m ≥ n, the network can tolerate any (m − n) faults in the middle stage while still realizing any permutation. This is a clean, mathematically proven guarantee — far simpler than the ad-hoc remapping required for asymmetric mesh topologies like Cerebras WSE.

The key insight: **all middle-stage switches are functionally interchangeable** (symmetric), so losing one merely reduces path diversity, not connectivity. In contrast, every node in a 2D mesh is topologically unique, making defect tolerance fundamentally harder.

## Fault Tolerance Mechanism

- **Strictly nonblocking (SNB):** C(m, n, r) is SNB when m ≥ 2n − 1. Any new connection can be made without disturbing existing ones. With m = 2n − 1 + k spare middle switches, the network tolerates k middle-stage failures while remaining SNB.
- **Rearrangeably nonblocking (RNB):** C(m, n, r) is RNB when m ≥ n. Tolerates (m − n) middle-stage faults. May need to rearrange existing connections, but all permutations remain realizable.
- **Input/output stage faults:** Can tolerate up to (m − 1) losing-contact faults in any single input/output stage switch.

## Recovery Algorithm (Rearrangement)

When a middle-stage switch fails or a new connection is blocked:
1. The route assignment is modeled as a **bipartite graph edge-coloring** problem.
2. Each middle-stage switch = one color. A faulty switch = a removed color.
3. Existing connections using the faulty switch must be **rearranged** (recolored) to use surviving switches.
4. Extra middle-stage switches provide additional colors, making the recoloring easier and faster.
5. The algorithm finds augmenting paths in the bipartite graph to reassign connections.

This is equivalent to: given a bipartite multigraph with maximum degree m, color edges with (m − f) colors where f is the number of faults. Possible whenever m − f ≥ n.

---

## Sources & Where They Mention It

### 1. "A Parallel Route Assignment Algorithm for Fault-Tolerant Clos Networks in OTN Switches" (IEEE, 2018)
- https://ieeexplore.ieee.org/abstract/document/8531701
- **Core result:** Route assignment for 3-stage fault-tolerant Clos modeled as edge-coloring. *"The three-stage fault-tolerant Clos network, where extra switch modules exist in the middle stage in case of switch failures, is widely used in the design of OTN switches."*
- **Extra switches as colors:** *"The extra switch modules provide additional colors for edge coloring, which help to reduce the running time of the coloring process remarkably."*
- **Practical application:** Used in Optical Transport Network (OTN) switch design.

### 2. "Topology and Routing Schemes for Fault-Tolerant Clos Network" (IEEE, 2009)
- https://ieeexplore.ieee.org/document/4908531/
- **Approach:** *"A new fault-tolerant Clos network is presented by adding extra switches and redirecting boxes in ordinary Clos network."*
- **Performance:** *"The extra switches and redirecting boxes can improve the run time of the routing algorithm significantly when the Clos network displays few or no faults."*

### 3. "A Fault-Tolerant Rearrangeable Permutation Network" (IEEE)
- https://www.researchgate.net/publication/3044748_A_fault-tolerant_rearrangeable_permutation_network
- **Beneš variant:** Adds redundancy to Beneš networks (recursive Clos) while preserving the recursive structure.
- **Fault model:** Analyzes non-contact faults (crosspoints stuck in uncontacted state due to hardware defects).

### 4. "Fault-tolerance for Switching Networks" (Springer)
- https://link.springer.com/chapter/10.1007/978-1-4613-0281-0_1
- **Comprehensive treatment** of redundancy strategies in multistage switching networks, including Clos.

### 5. "Nonblocking, Repackable, and Rearrangeable Clos Networks: Fifty Years of Theory Evolution" (IEEE)
- https://www.researchgate.net/publication/3199039_Nonblocking_repackable_and_rearrangeable_Clos_networks_Fifty_years_of_the_theory_evolution
- **Survey paper** covering 50 years of Clos network theory including fault tolerance analysis.

### 6. "The Number of Rearrangements in a 3-stage Clos Network Using an Auxiliary Switch" (Springer)
- https://link.springer.com/chapter/10.1007/978-1-4613-0281-0_8
- Analyzes rearrangement costs when using auxiliary (spare) switches.

### 7. "Waferscale Network Switches" (ISCA 2024) — Chen, Pal (Etched AI), Kumar (UIUC)
- http://passat.crhc.illinois.edu/isca24.pdf
- https://www.researchgate.net/publication/382813183_Waferscale_Network_Switches
- **Maps Clos logical topology onto physical mesh of sub-switch chiplets (SSCs) on a wafer.**
- Uses Tomahawk 5 as sub-switch chiplet baseline.
- *"A subset of inter-chiplet I/Os and a small fraction of chiplet area (<2%) would be used for feedthrough channels with repeaters."*
- Faulty SSC bypassed by rerouting through alternative middle-stage paths — symmetry provides multiple equivalent paths.

---

## Why Clos Fault Tolerance Is Even Simpler: No Deadlock Possible

Clos networks are **acyclic by construction** — data flows strictly input → middle → output. There are no cyclic dependencies possible in this topology. This means:

- **Conflicts (two connections sharing a middle switch) cause only congestion, never deadlock.** The worst case is performance degradation (queuing delay), not a system hang.
- **Recovery doesn't even require perfect edge-coloring.** You can simply route through any surviving middle switch and accept some congestion. No need to prove deadlock-freedom.
- **In contrast, 2D mesh rerouting around dead nodes can create turns that violate routing restrictions**, potentially introducing cycles in the channel dependency graph. This is why mesh-based systems need complex deadlock-avoidance schemes (e.g., submesh hierarchy routing with ascend-then-descend, no re-ascent constraints).

---

## Comparison: Clos (Symmetric) vs. Cerebras Mesh (Asymmetric)

| Aspect | Clos (symmetric) | Cerebras mesh (asymmetric) |
|--------|-------------------|----------------------------|
| **Redundancy model** | Extra middle-stage switches; math-proven tolerance | ~1–7% spare cores + mesh rerouting |
| **Fault impact** | Faulty switch removes one path; others equivalent | Faulty core distorts local topology |
| **Routing after fault** | Same algorithm, fewer colors — still nonblocking | Custom routing around dead cores |
| **Conflict behavior** | Congestion only (acyclic, no deadlock) | Can cause deadlock (cyclic dependencies) |
| **Recovery complexity** | Just pick any surviving switch; accept congestion | Must remap + prove deadlock-freedom |
| **Theory** | Well-established (Clos 1953, Beneš 1965) | Ad-hoc, architecture-specific |
| **Complexity** | O(N log N) rearrangement | NP-hard remapping in general |

---

## Key Takeaway for Paper

For symmetric topologies like Clos, fault tolerance is essentially a solved problem — add spare middle-stage switches, and because the topology is acyclic, you can even accept conflicts (congestion) without risk of deadlock. Recovery is trivial: reroute through any surviving middle switch. But for the 2D mesh topologies used in compute arrays (Cerebras WSE, systolic arrays), every node is topologically unique, rerouting can introduce deadlock, and defect tolerance is fundamentally harder. This motivates the need for a general-purpose virtual-to-physical remapping framework with deadlock-freedom guarantees (our contribution).
