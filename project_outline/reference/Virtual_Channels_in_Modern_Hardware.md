# Virtual Channels in Modern Hardware — Justification for ≥2 VC Assumption

## Summary

Our deadlock-free submesh hierarchy routing requires at least 2 virtual channels (VCs). This document collects concrete evidence that modern hardware provides far more than 2 VCs (or functional equivalents), making this a conservative assumption.

## Concrete Products

### 1. Cerebras WSE-2/WSE-3: 24 Virtual Channels ("Colors")

- **24 routable colors** (IDs 0–23), each a virtual communication channel for passing wavelets between PEs
- Each wavelet has a 5-bit tag encoding its color
- Colors are time-multiplexed onto the same physical links, non-blocking between one another
- "The congestion of one color does not block the traffic of another color"
- Each router has 24 independent static routes that can be configured
- Colors serve dual purpose: routing AND task activation (color determines what task consumes the wavelet)

**Source:** Cerebras SDK Documentation (v1.4.0), "A Conceptual View"
- https://sdk.cerebras.net/computing-with-cerebras
- https://sdk.cerebras.net/csl/language/task-ids

### 2. Intel Skylake-SP / Cascade Lake Mesh: 4 Ring Types (Effective Virtual Networks)

- The mesh interconnect uses 4 separate ring types, each carrying different message classes:
  - **AD ring** (Address/Data requests) — bidirectional
  - **AK ring** (Acknowledge) — bidirectional
  - **BL ring** (Block data / cache line transfers) — bidirectional
  - **IV ring** (Invalidate / snoop) — unidirectional
- Each ring type acts as a separate virtual network — messages on different rings don't block each other
- Additionally, each direction has "Even" and "Odd" lanes (A and B), effectively doubling the channels
- The CMS (Converged Mesh Stop) router manages injection/ejection/forwarding across these rings

**Source:** WikiChip, "Mesh Interconnect Architecture"
- https://en.wikichip.org/wiki/intel/mesh_interconnect_architecture

**Source:** Stefan1wan, "The Network-On-Chip Structure of Skylake and Congestion Monitoring"
- https://stefan1wan.github.io/2021/03/Skylake_NOC_functions/

**Source:** Miles Dai, "Reverse Engineering the Intel Cascade Lake Mesh Interconnect," MIT M.Eng. Thesis, 2021
- https://dspace.mit.edu/handle/1721.1/143928

### 3. ARM CMN-600/CMN-700 (AMBA CHI Protocol): 4 Channels

- The AMBA CHI (Coherent Hub Interface) protocol defines 4 separate channels:
  - **REQ** — Request channel
  - **RSP** — Response channel
  - **SNP** — Snoop channel
  - **DAT** — Data channel
- These are physically separate networks within the mesh — each crosspoint (XP) has independent routing for each channel
- CMN-600: configurable up to 8×8 mesh, each XP has 4 mesh ports + 2 device ports
- CMN-700: scalable up to 12×12 mesh (144 nodes)

**Source:** ARM Developer Documentation, "CHI Protocol Fundamentals"
- https://developer.arm.com/documentation/102407/latest/CHI-protocol-fundamentals

**Source:** AnandTech, "The CMN-700 Mesh Network"
- https://www.anandtech.com/show/16640/arm-announces-neoverse-v1-n2-platforms-cpus-cmn700-mesh/7

### 4. Google TPU (ICI): Multiple Virtual Channels

- TPU v4/v5/Ironwood use Inter-Chip Interconnect (ICI) in a 3D torus topology
- Each chip has 6 ICI links (±X, ±Y, ±Z)
- The ICI uses virtual channels for deadlock-free routing on the torus (torus routing inherently requires ≥2 VCs for deadlock freedom via dateline)
- TPU v5p: 4800 Gbps bisection bandwidth per chip

**Source:** Google Cloud Documentation, "TPU System Architecture"
- https://docs.cloud.google.com/tpu/docs/system-architecture-tpu-vm

### 5. Commercial Supercomputers (Historical)

- **Cray T3D/T3E:** 2 virtual channels for deadlock-free torus routing
- **IBM Blue Gene/L:** 2 virtual channels (separate for deterministic and adaptive routing)
- **Fujitsu Tofu (K computer / Fugaku):** Multiple virtual channels on 6D torus
- Dateline-based deadlock avoidance on torus networks requires minimum 2 VCs — all commercial torus-based systems implement at least this

**Source:** Wikipedia, "Wormhole Switching"
- https://en.wikipedia.org/wiki/Wormhole_switching

### 6. AMD Infinity Fabric: Proprietary (Likely ≥2 VCs)

- AMD's inter-die and inter-chiplet interconnect (Infinity Fabric / xGMI) connects CCD↔IOD and socket-to-socket
- Architecture details are proprietary; AMD does not publicly disclose VC counts
- Known: Infinity Fabric uses a coherent protocol with multiple message classes (similar to CHI), and supports adaptive routing on EPYC platforms
- Given that AMD uses torus-like topologies in multi-socket configurations and supports adaptive routing, ≥2 true VCs are likely (torus deadlock avoidance requires it), but this cannot be confirmed from public sources
- **Conclusion:** Cannot use as evidence for or against our ≥2 VC assumption due to insufficient public documentation

**Source:** AMD does not publish detailed Infinity Fabric microarchitecture. Partial information from:
- AMD EPYC processor architecture whitepapers (high-level block diagrams only)
- Various reverse-engineering efforts provide topology information but not VC details

### 7. NVIDIA GPU NoC: Crossbar-Based (Not Mesh with VCs)

- NVIDIA GPUs use a **crossbar interconnect** internally, not a 2D mesh with routers
- The crossbar connects SMs to L2 cache partitions and memory controllers
- A crossbar is a single-stage, fully-connected switch — there is no multi-hop routing, so the concept of VCs for deadlock avoidance does not directly apply
- For multi-GPU interconnect (NVLink/NVSwitch): NVSwitch is also a crossbar-based architecture; NVLink 4.0 provides 900 GB/s per GPU with NVSwitch 3.0
- **Conclusion:** NVIDIA's internal NoC architecture is fundamentally different from mesh-based systems. VCs are not applicable in the same way because there is no multi-hop routing within a single GPU. Not relevant to our ≥2 VC argument.

**Source:**
- Luo et al., "Benchmarking and Dissecting the Nvidia Hopper GPU Architecture," arXiv:2402.13499, 2024 (crossbar description)
- Lopes et al., "Uncovering Real GPU NoC Characteristics," MICRO 2024 (detailed GPU NoC reverse engineering — PDF not downloaded, behind ACM paywall)

## Adversary Case: Commercial Products WITHOUT Virtual Channels

An important question: are there real products with large-scale mesh/torus interconnects that achieve deadlock-free routing **without any VCs**? If so, our ≥2 VC requirement might seem unnecessarily restrictive.

### 1. Kalray MPPA-256 (Bostan): 256 cores, wormhole, explicitly 0 VCs
- **Strongest adversary case.** Explicitly documented as "wormhole switching without virtual channels."
- Deadlock avoidance via **Hamiltonian Odd-Even routing** (turn-model variant) on a regular 2D mesh.
- Routers contain only demultiplexers, output queues, and round-robin arbiters — minimal hardware.
- **Why it doesn't invalidate our assumption:** Kalray uses a **regular, defect-free mesh**. Turn-model routing guarantees reachability on regular meshes because enough alternative paths always survive turn restrictions. On a defective mesh, prohibited turns may be the **only** route around a fault — reachability breaks before deadlock is even a concern. Once you pre-compute routing tables to restore reachability (as we must), you need a separate deadlock-avoidance mechanism (like VCs).
- **Source:** De Dinechin et al., "Network-on-Chip Service Guarantees on the Kalray MPPA-256 Bostan Processor," DAC 2017.

### 2. SpiNNaker: 1M cores, no VCs, packet-dropping deadlock tolerance
- **Largest VC-free product.** 57,600 chips, ~1M ARM cores, triangular torus mesh.
- Explicitly: "virtual channels are not available in SpiNNaker" (area constraints).
- Uses **store-and-forward** switching (not wormhole) with small fixed-size packets (40 or 72 bits).
- Deadlock handling: **tolerates** rather than prevents deadlock — uses packet dropping and emergency rerouting when links block. "Makes no attempt to avoid loops."
- **Why it doesn't invalidate our assumption:** SpiNNaker is a **neuromorphic** platform where occasional packet loss is acceptable (neural spike traffic is inherently lossy). For deterministic compute workloads (GEMM, GEMV), packet dropping is unacceptable — correctness requires guaranteed delivery. Our domain demands deadlock **prevention**, not tolerance.
- **Source:** Navaridas et al., "SpiNNaker: Enhanced multicast routing," Parallel Computing, 2015.

### 3. Adapteva Epiphany: 64 cores (scalable to 4096), 3 physically separate mesh networks
- No per-router VCs, but uses **3 independent physical mesh networks** (rmesh, cmesh, xmesh) for different traffic classes.
- Deadlock freedom via XY dimension-order routing on each regular mesh + traffic separation across physical networks.
- **Why it doesn't invalidate our assumption:** Multiple physical networks are **at least as expensive** as VCs in area/wiring — they replace VC multiplexing with full physical replication. Also relies on regular mesh topology.
- **Source:** Adapteva Epiphany Architecture Reference Manual.

### 4. Tilera TILE64/TILE-Gx: 64–72 cores, 5 physically separate mesh networks
- Similar to Epiphany: 5 independent 2D mesh networks (MDN, UDN, TDN, IDN, STN), each for a different traffic type.
- XY wormhole routing per network; traffic separation prevents protocol deadlock.
- **Same argument:** Multiple physical networks ≈ same cost as VCs. Regular mesh only.
- **Source:** Wentzlaff et al., "On-Chip Interconnection Architecture of the Tile Processor," IEEE Micro, 2007.

### Defect Handling in VC-Free Products

None of these products solve the irregular-topology-after-defect problem:

**Tilera TILE-Gx72 — single die, on-chip mesh only.**
- 72 cores on one die (40nm), 8×9 mesh. The iMesh does NOT extend across chip boundaries.
- Yield binning: fuse off edge cores to sell as lower SKUs (72→36→16→9), preserving a regular rectangular sub-mesh.
- Interior router defect → discard entire die.
- Source: Wikipedia "TILE-Gx"; Semiaccurate 2013 announcement.

**Kalray MPPA-256 — single die, NoC connects clusters not cores.**
- 256 PE cores across 16 compute clusters on one die (28nm). NoC is a 2D **torus** (not mesh) with 32 nodes at cluster granularity.
- A faulty core inside a cluster doesn't affect NoC topology. A faulty cluster-level router → discard die.
- Has "off-chip extensions" mentioned in literature but primarily a single-die SoC.
- Source: De Dinechin et al., DAC 2017; Kalray CERN presentation.

**Adapteva Epiphany — single die, BUT eMesh designed for multi-chip extension.**
- Epiphany-IV: 64 cores on one die (28nm). Epiphany-V: 1024 cores on one die (16nm).
- **Critical: the eMesh was explicitly designed to extend across chip boundaries** — 4 LVDS links (N/S/E/W) per chip, up to 64 chips connected in a seamless 2D mesh with flat global addressing.
- Uses 3 physically separate mesh networks, XY dimension-order routing, **no VCs**.
- **No documented defect-tolerance mechanism for multi-chip topology.** If a chip in the middle of a multi-chip Epiphany system dies, the eMesh has a hole → XY routing breaks → no known solution. This problem was apparently never addressed.
- Source: Adapteva Epiphany Architecture Reference Manual; Olofsson, "Epiphany-V: A 1024-core 64-bit RISC SoC," arXiv:1610.01832, 2016.

**SpiNNaker — multi-chip, triangular torus.**
- 57,600 chips (each 18 cores, 130nm), connected in a 2D triangular torus (6 links per chip).
- Topology extends across chips and boards via spiNNlink FPGA bridges.
- Dead chip → **lossy tolerance**: packet dropping + emergency rerouting through triangle edges. "Makes no attempt to avoid loops."
- Has spare cores (1 of 18 per chip) for intra-chip fault tolerance.
- Source: Navaridas et al., "SpiNNaker: Enhanced multicast routing," Parallel Computing, 2015; Furber et al., "Overview of the SpiNNaker System Architecture," IEEE TC, 2013.

### Summary: Why None Invalidate Our ≥2 VC Assumption

| Product | Scale | Single/Multi-Die | VC-Free Strategy | Defect Handling | Why Not Applicable |
|---------|-------|-------------------|-----------------|-----------------|-------------------|
| **Kalray MPPA-256** | 256 cores | Single die | Turn-model on regular torus | Discard die | Regular topology only |
| **SpiNNaker** | 1M cores | Multi-chip | Packet dropping | Lossy tolerance | Unacceptable for deterministic compute |
| **Adapteva Epiphany** | 64–4096 cores | Single die, multi-chip extensible | 3 physical networks + XY routing | **None for multi-chip** — hole in mesh breaks XY routing | Unsolved problem; no VCs to fall back on |
| **Tilera TILE64** | 64–72 cores | Single die | 5 physical networks + XY routing | Yield binning (edge fuse-off) or discard | Regular sub-mesh only |

**Key insight:** Every VC-free product either (a) is single-die and discards the die on interior defects, (b) tolerates packet loss (unacceptable for deterministic compute), or (c) has a multi-chip extensible mesh but **never solved** the irregular-topology-after-defect problem (Adapteva). The only products that actually handle interior defects in multi-die meshes — Cerebras (24 VCs), Google TPU (≥2 VCs) — all use virtual channels. Our ≥2 VC requirement is the inherent cost of choosing utilization over waste.

## Academic Reference

### "Determining the Minimum Number of Virtual Networks for Different Coherence Protocols"
- **Authors:** Weihang Li, Andrés Goens, Nicolai Oswald, Vijay Nagarajan, Daniel J. Sorin
- **Venue:** ISCA 2024
- **Key finding:** The conventional wisdom that VN count = longest message dependency chain is "neither necessary nor sufficient." They develop a formal methodology to compute the true minimum. The answer varies by protocol, but all practical coherence protocols require ≥2 virtual networks.
- https://ieeexplore.ieee.org/document/10609584/

## Important Distinction: True VCs vs. Protocol-Level Virtual Networks

**True virtual channels** are general-purpose, fungible, and reassignable by the routing algorithm:
- Any VC can carry any message type
- Multiplexed on the same physical link
- The routing algorithm decides which VC to use for deadlock avoidance

**Protocol-level virtual networks** are dedicated channels for specific message classes:
- Each network carries only one message type (e.g., requests, responses, data)
- Cannot be reassigned by the routing algorithm
- Exist to avoid protocol-level deadlocks in coherence transactions, not for routing flexibility

**Intel Skylake-SP (AD/AK/BL/IV) and ARM CHI (REQ/RSP/SNP/DAT) are protocol-level virtual networks, NOT true VCs.** They cannot be used to justify our ≥2 VC assumption because our routing algorithm needs to assign VCs to ascending/descending phases — this requires general-purpose, reassignable VCs.

## Summary Table

| Platform | Year | True VCs? | Count | Mechanism |
|----------|------|-----------|-------|-----------|
| Cerebras WSE-2/3 | 2021–2024 | **Yes** | **24** colors | Any color carries any data; time-multiplexed, non-blocking |
| Google TPU v4+ (ICI) | 2022+ | **Yes** | **≥2** | Dateline-based deadlock-free torus routing |
| Cray T3D/T3E | 1993–1996 | **Yes** | **2** | Dateline VC for torus deadlock avoidance |
| IBM Blue Gene/L | 2004 | **Yes** | **2** | Separate VCs for deterministic + adaptive routing |
| Intel Skylake-SP mesh | 2017 | **No** (protocol VNs) | 4 ring types | AD/AK/BL/IV — each dedicated to a message class |
| ARM CMN-600/700 (CHI) | 2019–2021 | **No** (protocol VNs) | 4 channels | REQ/RSP/SNP/DAT — each dedicated to a message type |
| AMD Infinity Fabric | 2017+ | **Unknown** (proprietary) | Unknown | Likely ≥2 (torus topology requires it), but not publicly documented |
| NVIDIA GPU NoC | 2016+ | **N/A** (crossbar) | N/A | Single-stage crossbar, no multi-hop routing → VCs not applicable |

**Conclusion:** Architectures with true VCs (Cerebras, TPU, Cray, Blue Gene) all provide ≥2. Cerebras provides 24. Our assumption of ≥2 VCs is conservative for any architecture that supports general-purpose virtual channels. For architectures that only have protocol-level virtual networks (Intel, ARM), additional true VCs would be needed to support our routing scheme — but these systems also typically do not expose a raw 2D mesh to user workloads in the way our remapper targets. AMD and NVIDIA internal NoC details are proprietary or use fundamentally different architectures (crossbar), so they neither support nor contradict our assumption.

**On the adversary case:** Turn-model routing achieves deadlock freedom on regular meshes without VCs, but on defective meshes, prohibited turns may be the only route around a fault — breaking **reachability**, not just deadlock freedom. Pre-computing routing tables to restore reachability then requires a separate deadlock-avoidance mechanism (like VCs), bringing us back to the ≥2 VC requirement.
