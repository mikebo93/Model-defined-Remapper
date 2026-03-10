# MICRO 2026 Paper Preparation Guide
## Topic: Virtual Topology Mapping to Physical Topology

---

## 1. Conference & Deadlines

- **Conference:** MICRO-59 — 59th IEEE/ACM International Symposium on Microarchitecture
- **Location:** Athens, Greece
- **Conference Dates:** October 31 - November 4, 2026
- **Website:** https://www.microarch.org/micro59/

| Milestone | Date |
|---|---|
| Abstract submission | March 31, 2026 (11:59 PM EDT) |
| Full paper submission | April 7, 2026 (11:59 PM EDT) |
| Rebuttal/revision period | June 3-17, 2026 |
| Author decisions | July 7, 2026 |

---

## 2. Submission Format & Guidelines

### Page & Layout
- **Page limit:** 11 pages max (single-spaced, two-column), references unlimited
- **Page size:** US Letter (8.5" x 11")
- **Margins:** Top/Bottom 1", Left/Right 0.75"
- **Column spacing:** 0.25"
- **Appendices:** NOT allowed

### Typography
- **Body font:** Times, 9pt minimum, 11pt leading
- **Section headings:** 12pt
- **Subsection headings:** 10pt
- **Captions:** 9pt minimum
- **References font:** 8pt

### Submission
- **File format:** Printable PDF only
- **Template:** LaTeX template from MICRO 2026 website (strongly encouraged)
- **Page numbers:** Required
- **Confidentiality banner:** Must appear on title page with submission number
- **References:** Must list all authors (no "et al.")
- **Figures/tables:** Must be legible in grayscale (many reviewers print in B&W)

### Formatting Restrictions
- No space-squeezing (no `\vspace` or vertical space manipulation packages)
- Submissions violating format policy may be rejected without review, even if they pass HotCRP format check

### Double-Blind Review
- No author names on submitted documents
- PDF metadata must not reveal authorship
- All artifact links must be anonymized or removed
- No acknowledgments of persons or funding agencies

### Dual Submission Policy
- No significant overlap with papers under review elsewhere
- Exceptions: workshops without archived proceedings, arXiv, IEEE CAL
- All authors must be declared upfront; changes after acceptance require PC chair approval

### Tracks
- **Research Track** - traditional research papers
- **Industry Track** (new/inaugural) - deep technical insights from production-focused architectural work

---

## 3. Relevant & Impactful Papers to Study

### Core NoC / Topology Mapping Papers

| Paper | Venue | Key Contribution |
|-------|-------|-----------------|
| Modular Routing Design for Chiplet-based Systems (Yin et al.) | ISCA | Composable, topology-agnostic, deadlock-free routing for chiplets |
| NN-Baton: DNN Workload Orchestration and Chiplet Granularity Exploration for Multichip Accelerators | ISCA 2021 | Workload-to-chiplet mapping optimization |
| Kite: Heterogeneous Interposer Topologies via Accurate Interconnect Modeling | DAC 2020 | Family of heterogeneous topologies for chiplet integration |
| Chipletizer: Repartitioning SoCs for Cost-Effective Chiplet Integration | ASPDAC 2024 | Design automation for chiplet partitioning |
| GIA: A Reusable General Interposer Architecture for Agile Chiplet Integration | ICCAD 2022 | General interposer architecture |
| vNPU: Topology-Aware Virtualization over Inter-Core Connected NPUs | arXiv 2025 | Virtual topology creation + best-effort topology mapping |
| TPNoC: Efficient Topology Reconfigurable NoC Generator | GLSVLSI 2023 | Reconfigurable NoC topology generation |
| A Scalable NoC Topology Targeting Network Performance | NoCArc @ MICRO 2021 | Scalable topology design considering path diversity and bisection width |

### Recommended Search Venues
- **MICRO** proceedings (IEEE/ACM): https://dl.acm.org/conference/micro
- **ISCA** proceedings: https://dl.acm.org/conference/isca
- **NoCArc Workshop** (co-located with MICRO): Primary venue for NoC topology research
- **HPCA, ASPLOS, DAC, ICCAD**: Adjacent architecture/design conferences
- **IEEE Micro Top Picks**: Recognizes most impactful architecture papers annually

### Suggested Search Queries
- "virtual topology mapping physical topology NoC" on Google Scholar
- "chiplet network topology optimization" on IEEE Xplore
- "network-on-chip application mapping" on ACM Digital Library
- "topology-aware virtualization accelerator" on arXiv

---

## 4. How to Write a Strong MICRO Paper

### Simon Peyton Jones' Seven Suggestions

1. **Don't wait — write.** Writing crystallizes your thinking and reveals gaps in understanding.
2. **Identify your key idea.** Every paper should have one clear, sharp idea you can state in one sentence.
3. **Tell a story.** Structure: problem -> why it's hard -> your insight -> your solution -> evidence it works.
4. **Nail your contributions.** State them explicitly in the intro. Be specific ("We reduce latency by 35%"), not vague.
5. **Put related work later.** Introduce your approach first, then contrast with prior work.
6. **Put your readers first.** Use examples early. A running example in Section 2 is worth more than pages of formalism.
7. **Listen to your readers.** Get feedback early and often.

### What MICRO/ISCA Reviewers Evaluate

- **Novelty:** Is this a genuinely new idea or a marginal extension?
- **Readability:** Is the paper clear, well-organized, and self-contained?
- **Experimental methodology:** Reasonable benchmarks? Appropriate simulation/modeling? Are assumptions justified?
- **Significance of results:** Do the improvements matter in practice?
- **Relevance to community:** Will this spark discussion and follow-up work?

### Architecture Paper Structure (Recommended)

1. **Introduction** (1.5-2 pages): Motivation, problem statement, key insight, contributions list
2. **Background & Motivation** (1-1.5 pages): Context, motivating example/data showing the problem is real
3. **Design / Architecture** (3-4 pages): Your proposed solution in detail
4. **Implementation** (0.5-1 page): How you built/simulated it
5. **Evaluation** (2.5-3 pages): Methodology, benchmarks, results, analysis
6. **Related Work** (0.5-1 page): Contrast with prior approaches
7. **Conclusion** (0.5 page): Summary and future directions

### Common Pitfalls to Avoid

- **No clear problem statement** — reviewers need to understand WHY this matters in the first two paragraphs
- **Weak baselines** — always compare against state-of-the-art, not just naive approaches
- **Overclaiming** — be precise about what you did and didn't show
- **Poor figures** — architecture papers live and die by their diagrams
- **Ignoring scalability** — MICRO reviewers care about whether your approach generalizes
- **Missing sensitivity analysis** — show how results change with key parameters
- **Squeezing formatting** — reviewers notice and it creates a negative impression

### Tips Specific to Topology Mapping Papers

- Show the mapping problem is NP-hard or computationally challenging (motivates your heuristic/algorithm)
- Provide visual diagrams of both virtual and physical topologies
- Evaluate across multiple topology sizes and configurations
- Report latency, throughput, energy, and area (multi-metric evaluation)
- Compare against both optimal (ILP) solutions at small scale and heuristics at large scale
- Consider real workload traces, not just synthetic traffic patterns

---

## 5. Topics of Interest (MICRO 2026)

- Performance optimization and energy efficiency
- Security, privacy, and reliability
- Processor and memory architectures
- Parallelism techniques
- Cloud, datacenter, and embedded computing
- Accelerator-based and reconfigurable designs
- Emerging technologies and quantum computing
- Memory hierarchy and interconnection networks
- Benchmarking and evaluation methodologies

---

## 6. Key Resources & Links

- MICRO 2026 Home: https://microarch.org/micro59/
- MICRO 2026 Submission Guidelines: https://www.microarch.org/micro59/submit/guidelines.php
- MICRO 2026 Call for Papers: https://www.microarch.org/micro59/submit/papers.php
- SIGMICRO Awards & Test of Time: https://www.sigmicro.org/awards/tot/
- Simon Peyton Jones — Writing Tips: https://simon.peytonjones.org/great-research-paper/
- Jeff Huang — Best Paper Awards in CS: https://jeffhuang.com/best_paper_awards/
- ACM Digital Library (MICRO proceedings): https://dl.acm.org/conference/micro
