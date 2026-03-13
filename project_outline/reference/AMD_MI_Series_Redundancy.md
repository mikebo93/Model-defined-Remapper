# AMD Instinct MI Series — Redundant Compute Units for Yield

## Summary

AMD builds extra CUs into each compute die and disables a few per die for yield harvesting.

| Product | Arch | Physical CUs/die | Enabled CUs/die | Disabled | Dies/pkg | Total Enabled |
|---------|------|-------------------|-----------------|----------|----------|---------------|
| MI250X  | CDNA 2 | 112 per GCD | 110 per GCD | 2 | 2 GCDs | 220 |
| MI300X  | CDNA 3 | 40 per XCD  | 38 per XCD  | 2 | 8 XCDs | 304 |

---

## Sources & Where They Mention It

### MI300X (CDNA 3)

1. **ROCm Documentation — MI300 Microarchitecture**
   - https://rocm.docs.amd.com/en/latest/conceptual/gpu-arch/mi300.html
   - States: *"The XCD has 40 CUs: 38 active CUs at the aggregate level and 2 disabled CUs for yield management."*
   - Found in the XCD-level system architecture section.

2. **Chips and Cheese — "AMD's CDNA 3 Compute Architecture"**
   - https://chipsandcheese.com/p/amds-cdna-3-compute-architecture
   - States: *"every XCD physically has 40 CDNA 3 Compute Units, with 38 of these being enabled per XCD on the MI300X."*
   - Found in the section describing the XCD layout.

3. **AMD Hot Chips 2024 Presentation — MI300X (PDF)**
   - https://hc2024.hotchips.org/assets/program/conference/day1/23_HC2024.AMD.MI300X.ASmith(MI300X).v1.Final.20240817.pdf
   - Official AMD slide deck; should contain XCD block diagram showing 40 CUs with 38 enabled.

### MI250X (CDNA 2)

4. **TechPowerUp — "AMD Releases CDNA2 MI250X Aldebaran HPC GPU Block Diagram"**
   - https://www.techpowerup.com/298100/amd-releases-its-cdna2-mi250x-aldebaran-hpc-gpu-block-diagram
   - States: *"The eight Shader Engines total 112 Compute Units, or 14 CU per engine."* (physical count per GCD)
   - Does not explicitly state 110 enabled, but the physical count is 112 per GCD.

5. **ROCm Documentation — MI250 Microarchitecture**
   - https://rocm.docs.amd.com/en/latest/conceptual/gpu-arch/mi250.html
   - States: *"The MI250 GCD has 104 active CUs."* (uses "active" — implies others disabled)
   - Note: MI250 has 104 active; MI250**X** has 110 active per GCD (higher-bin part).

6. **AMD Official Product Page — MI250X**
   - https://www.amd.com/en/products/accelerators/instinct/mi200/mi250x.html
   - Lists 220 total compute units (= 110 per GCD x 2 GCDs). Physical is 112 per GCD.

7. **Chips and Cheese — "Hot Chips 34: AMD's Instinct MI200 Architecture"**
   - https://chipsandcheese.com/2022/09/18/hot-chips-34-amds-instinct-mi200-architecture/
   - Describes GCD internal layout: 4 compute engines x 2 shader engines x 14 CUs = 112 CUs per GCD.
   - Does not explicitly call out disabled CUs, but the math (112 physical vs 110 enabled) shows 2 harvested.

8. **AMD CDNA 2 White Paper (PDF)**
   - https://www.amd.com/content/dam/amd/en/documents/instinct-business-docs/white-papers/amd-cdna2-white-paper.pdf
   - Official architecture white paper for CDNA 2. Should contain GCD CU counts.

### General

9. **ORNL Frontier Training — MI250X Slides (PDF)**
   - https://www.olcf.ornl.gov/wp-content/uploads/Public-AMD-Instinct-MI-250X-Frontier-8.23.23.pdf
   - Oak Ridge National Lab presentation on MI250X used in Frontier supercomputer.
