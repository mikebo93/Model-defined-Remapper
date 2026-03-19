# Remapper Codebase Summary

## Overview

The Remapper is a Rust-based tool for mapping virtual (ideal) 2D mesh NoC topologies onto faulty physical meshes. It enables applications to transparently execute on degraded hardware by discovering heuristic virtual-to-physical coordinate mappings while accounting for faults and maintaining application communication patterns. The underlying graph embedding problem is NP-hard (generalizes subgraph isomorphism with cost minimization), so the mapper uses hierarchical spatial search heuristics rather than exact solvers.

- **GitHub source:** `Remapper/` (symlinked from `../Remapper`)
- **Language:** Rust (workspace with 7 modules)

---

## Module Architecture

### Common (`Common/src/lib.rs`)
Shared type definitions and utilities across modules.

### Util (`Util/src/`)
- **graph.rs** — Generic graph abstractions (NodeTrait, GraphTrait)
- **random.rs** — Seeded ChaCha20 RNG for reproducibility
- **ref_type.rs** — Thread-safe/single-threaded reference wrappers

### IR: Intermediate Representation (`IR/src/`)
Defines the computational model applications express:
- **task.rs** — Three task types: SendTask, ReceiveTask, ProcessTask (per-actor dependency DAGs)
- **work.rs** — Eight work types: UnicastWork, MulticastWork, ProcessWork, ClusterProcessWork, ReduceWork, GatherWork, AllToAllWork, CustomGroupWork
- IR abstracts away specific NoC topology; applications define work graphs that constrain communication patterns

### NoC: Network-on-Chip (`NoC/src/`)
Models physical and virtual mesh topologies:
- **mesh.rs** — Standard 4-connected 2D mesh (N/S/E/W)
- **diagonal_mesh.rs** — 8-connected mesh with diagonal links (NE/NW/SE/SW)
- **light_mesh.rs / light_diagonal_mesh.rs** — Flat-array variants for large meshes (512x512+)
- **Routing:** XY dimension-order routing (mesh), diagonal XY (8-connected)
- **Workflow builders:** mesh_gemm (systolic), step_mesh_gemm (tiled), mesh_gemv (broadcast+reduce)
- **Predictor:** Wormhole pipelining latency model with congestion awareness (Best/Average/Worst)

### Mapper: Core Remapping Engine (`Mapper/src/`)

**Data Structures:**
- **MeshMapping** — Bidirectional coord maps (virtual <-> physical), cost tracking, frontier state
- **Submesh** — Rectangular partitions of physical mesh
- **SuperNode** — Groupings of nearby submeshes for hierarchical KdTree search
- **CandidatePool** — Available physical locations per-submesh

**Partitioning:**
- Recursive Coordinate Bisection (RCB) that respects faults
- Builds submesh adjacency graph and super node KdTree for spatial lookup

**Mapping Algorithm Pipeline:**
```
map()
  -> partition()              [RCB + super nodes]
  -> map_topology()           [main iterative loop]
     -> init_anchor_coords()  [seed with best starting point]
     -> loop expand_mapping() [frontier expansion]
```

**Frontier Expansion (expand_mapping):**
1. Identify unmapped virtual coords adjacent to frontier
2. Two-level hierarchical candidate search:
   - Level 1: KdTree query for nearest super nodes
   - Level 2: Evaluate submesh centres, pick top-K
3. Evaluate candidates in parallel (rayon), select by cost
4. Commit mapping, update frontiers, prune consumed candidates

**Cost Model:**
- Coordinate cost (local mapping consistency, 2-hop lookahead)
- RANSAC geometric consistency check
- Hop cost with LinkUsage congestion tracking
- Workflow-aware cost (communication pattern analysis)
- Supports Manhattan (4-connected) and Chebyshev (8-connected) distance metrics

**Routing & Deadlock Freedom:**
- Submesh hierarchy routing: ascend-then-descend constraint (no re-ascent)
- Routing paths respect submesh hierarchy -> deadlock-free by construction
- RoutingDatabase caches full physical paths
- Arborescence/BFS routing tree construction for multicast patterns

### Simulator (`Simulator/src/`)
- **Full simulator** — Rc/RefCell, trait-based, cycle-accurate
- **Light simulator** — Flat arrays for large meshes (512x512+)
- Supports store-and-forward and wormhole routing, virtual channels

### Experiments (`Experiments/src/main.rs`)
1. Healthy mesh baseline prediction (3 congestion modes)
2. Defective mesh + remapping + prediction
3. Workloads: GEMM (systolic) and GEMV (broadcast/reduce)
4. Output: JSON with per-submesh stats and timing

---

## Experiment Configuration

Key parameters (from `config_large.json`):
- `bandwidth_per_cycle`: 32 bits/cycle
- `flops_per_pu_per_cycle`: 16
- `hop_latency_cycles`: 1.0
- `defective_mesh_factor`: 1.5 (physical = virtual * 1.5)
- Fault rates: PU 7%, Router 3.5%, Channel 0.7%
- Mapper: max_block_size=4, search_nearest_n=5, search_top_k=3, expansion_trials=10

## Tested Scenarios
- **Mesh-to-Mesh:** Regular 4-connected virtual mesh -> faulty 4-connected physical mesh
- **Mesh-to-DiagonalMesh:** Regular 4-connected virtual mesh -> faulty 8-connected physical mesh (demonstrates unused diagonal link utilization)
- Scale: up to 512x512 virtual meshes

---

## Key Source Files

| Function | File |
|----------|------|
| Mapping entry | `Mapper/src/mapper/mesh_mapper.rs` |
| Cost model | `Mapper/src/mapper/cost_model/common.rs` |
| Deadlock-free routing | `Mapper/src/routing/common.rs` |
| Routing database | `Mapper/src/routing/routing_database.rs` |
| Mesh topology | `NoC/src/noc/mesh.rs` |
| Diagonal mesh | `NoC/src/noc/diagonal_mesh.rs` |
| XY routing | `NoC/src/routing/xy.rs` |
| Experiments | `Experiments/src/main.rs` |
| Configs | `Exp/RemappedExperiment/config_large.json` |
