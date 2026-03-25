# Maximum Defect-Free Region on a Wafer-Scale Mesh: Theory and Derivations

---

# Part I — Background: 1D and Continuous Theory

## 1. Warm-Up: Single Point on a Continuous Interval

### Setup

Let $X \sim \text{Uniform}(0,1)$. The distances to the two endpoints are $X$ (left) and $1-X$ (right). The maximum distance is:

$$M = \max(X,\; 1-X)$$

The range of $M$ is $[1/2, 1]$, since the longer side is always at least half.

### CDF

$$P(M \leq m) = P(\max(X, 1-X) \leq m) = P(X \leq m \text{ and } 1-X \leq m)$$
$$= P(1-m \leq X \leq m) = m - (1-m) = 2m - 1$$

for $m \in [1/2, 1]$.

### PDF

$$f_M(m) = \frac{d}{dm}(2m-1) = 2, \quad m \in [1/2, 1]$$

### Result

$$M \sim \text{Uniform}(1/2, 1)$$

**Intuition:** The original $X$ is uniform on $[0,1]$. Taking $\max(X, 1-X)$ "folds" the interval at $1/2$, mapping $[0, 1/2)$ onto $(1/2, 1]$. The density doubles (from 1 to 2) and the domain halves (from length 1 to $1/2$).

---

## 2. Maximum Spacing of $n$ Uniform Points

### Setup

$n$ i.i.d. points $U_1, \ldots, U_n \sim \text{Uniform}(0,1)$. Order statistics: $U_{(1)} \leq \cdots \leq U_{(n)}$. This creates $n+1$ spacings:

$$D_0 = U_{(1)}, \quad D_i = U_{(i+1)} - U_{(i)} \text{ for } i=1,\ldots,n-1, \quad D_n = 1 - U_{(n)}$$

We want the distribution of $M_n = \max(D_0, D_1, \ldots, D_n)$.

### Derivation via Inclusion-Exclusion

Define events $A_i = \{D_i > m\}$ for $i = 0, 1, \ldots, n$. Then:

$$P(M_n \leq m) = P(\text{all spacings} \leq m) = 1 - P\!\left(\bigcup_{i=0}^{n} A_i\right)$$

Using the compression argument (Section 4), any $k$ specified spacings simultaneously exceeding $m$ has probability $(1-km)^n$, independent of which $k$ are chosen. Applying inclusion-exclusion (Section 3):

$$P\!\left(\bigcup_{i=0}^{n} A_i\right) = \sum_{k=1}^{n+1} (-1)^{k+1} \binom{n+1}{k}(1-km)^n$$

Absorbing the leading 1 as the $k=0$ term:

$$\boxed{F_{M_n}(m) = \sum_{k=0}^{\lfloor 1/m \rfloor} (-1)^k \binom{n+1}{k}(1-km)^n, \quad m \in \left[\frac{1}{n+1},\; 1\right]}$$

Here $F_{M_n}(m) = P(M_n \leq m)$ is the cumulative distribution function (CDF) of the maximum spacing. The upper limit $\lfloor 1/m \rfloor$ is a natural truncation: when $km > 1$, the term $(1-km)^n$ is zero.

### PDF

Differentiating:

$$f_{M_n}(m) = n \sum_{k=1}^{\lfloor 1/m \rfloor} (-1)^{k+1} \binom{n+1}{k}\, k\, (1-km)^{n-1}$$

### Expected Value

$$\boxed{E[M_n] = \frac{H_{n+1}}{n+1}}$$

where $H_{n+1} = \sum_{j=1}^{n+1} \frac{1}{j}$ is the harmonic number. Asymptotically, $E[M_n] \sim \frac{\ln n}{n}$.

### Properties

- **Support:** $M_n \in [1/(n+1), 1]$. The lower bound follows from the pigeonhole principle: $n+1$ spacings summing to 1 means the largest is at least the average.
- **Piecewise polynomial:** The CDF has breakpoints at $m = 1/j$ for $j = 2, 3, \ldots, n+1$, since the number of non-zero terms in the sum changes at each threshold.

### Verification ($n=1$)

For $m \in [1/2, 1]$, $\lfloor 1/m \rfloor = 1$:

$$F_{M_1}(m) = \binom{2}{0}(1)^1 - \binom{2}{1}(1-m)^1 = 1 - 2(1-m) = 2m - 1$$

This matches Section 1. $\checkmark$

---

## 3. Inclusion-Exclusion Principle: Full Proof

### Statement

For any $N$ events $A_1, \ldots, A_N$:

$$P\!\left(\bigcup_{i=1}^{N} A_i\right) = \sum_{k=1}^{N} (-1)^{k+1} \sum_{1 \leq i_1 < \cdots < i_k \leq N} P(A_{i_1} \cap \cdots \cap A_{i_k})$$

### Notation

The inner sum $\displaystyle\sum_{1 \leq i_1 < i_2 < \cdots < i_k \leq N}$ means: choose $k$ distinct indices from $\{1, 2, \ldots, N\}$ in increasing order, and sum over all $\binom{N}{k}$ such choices. The constraint $i_1 < i_2 < \cdots < i_k$ ensures each combination is counted exactly once.

**Concrete example ($N = 4$):**

- $k=1$: $\binom{4}{1} = 4$ terms — $P(A_1) + P(A_2) + P(A_3) + P(A_4)$
- $k=2$: $\binom{4}{2} = 6$ terms — $P(A_1 \cap A_2) + P(A_1 \cap A_3) + P(A_1 \cap A_4) + P(A_2 \cap A_3) + P(A_2 \cap A_4) + P(A_3 \cap A_4)$
- $k=3$: $\binom{4}{3} = 4$ terms — $P(A_1 \cap A_2 \cap A_3) + P(A_1 \cap A_2 \cap A_4) + P(A_1 \cap A_3 \cap A_4) + P(A_2 \cap A_3 \cap A_4)$
- $k=4$: $\binom{4}{4} = 1$ term — $P(A_1 \cap A_2 \cap A_3 \cap A_4)$

### Proof

**Strategy:** Show every sample point $\omega$ in the union is counted exactly once by the right-hand side.

Suppose $\omega$ belongs to exactly $r$ of the $N$ events ($r \geq 1$). WLOG, $\omega \in A_1, \ldots, A_r$. At level $k$, an intersection $A_{i_1} \cap \cdots \cap A_{i_k}$ contains $\omega$ iff all $k$ indices are among $\{1, \ldots, r\}$. The number of such intersections is $\binom{r}{k}$.

Total count of $\omega$:

$$C(r) = \sum_{k=1}^{r} (-1)^{k+1} \binom{r}{k}$$

By the binomial theorem at $x = -1$:

$$(1-1)^r = \sum_{k=0}^{r} \binom{r}{k}(-1)^k = 0$$

$$1 + \sum_{k=1}^{r}(-1)^k \binom{r}{k} = 0 \implies \sum_{k=1}^{r} (-1)^{k+1} \binom{r}{k} = 1$$

So $C(r) = 1$ for all $r \geq 1$. Every point in the union is counted exactly once. $\blacksquare$

### Why the Alternating Sign Works: Numerical Example ($r=4$)

| $k$ | Sign $(-1)^{k+1}$ | Terms $\binom{4}{k}$ | Running total |
|---|---|---|---|
| 1 | $+$ | 4 | 4 |
| 2 | $-$ | 6 | $4 - 6 = -2$ |
| 3 | $+$ | 4 | $-2 + 4 = 2$ |
| 4 | $-$ | 1 | $2 - 1 = \mathbf{1}$ |

The alternating sum always converges to 1, regardless of $r$.

### Application to Spacings

With $N = n+1$ spacings, all $\binom{n+1}{k}$ intersection probabilities at level $k$ are equal to $(1-km)^n$ (by exchangeability). This collapses the double sum:

$$\sum_{1 \leq i_1 < \cdots < i_k \leq n+1} P(A_{i_1} \cap \cdots \cap A_{i_k}) = \binom{n+1}{k} \cdot (1-km)^n$$

---

## 4. The Compression Argument

### Claim

For $n$ uniform points on $[0,1]$, the probability that any $k$ specified spacings each exceed $m$ is $(1-km)^n$, independent of which $k$ are chosen.

### Proof

**Step 1 — Spacings are exchangeable.** The $n+1$ spacings $(D_0, \ldots, D_n)$ follow a symmetric Dirichlet$(1,1,\ldots,1)$ distribution — the uniform distribution on the $n$-simplex $\{d_i \geq 0 : \sum d_i = 1\}$. Any subset of $k$ spacings has the same joint distribution.

**Step 2 — Variable substitution.** Require $k$ spacings $D_{i_1}, \ldots, D_{i_k} > m$. Define:

$$D'_{i_j} = D_{i_j} - m \geq 0 \quad \text{(for each of the } k \text{ specified spacings)}$$
$$D'_i = D_i \geq 0 \quad \text{(for the remaining spacings)}$$

These satisfy $\sum D'_i = 1 - km$, all non-negative — equivalent to $n$ points on an interval of length $1 - km$.

**Step 3 — Volume ratio.** The $n$-simplex $\{x_i \geq 0 : \sum x_i = L\}$ has volume $\propto L^n$:

$$P(D_{i_1} > m, \ldots, D_{i_k} > m) = \frac{(1-km)^n}{1^n} = (1-km)^n$$

### Concrete Example ($n=3$, $k=2$, $m=0.2$)

Three points, four spacings $D_0, D_1, D_2, D_3$. Want $P(D_0 > 0.2 \text{ and } D_2 > 0.2)$.

1. $D_0 > 0.2$: the region $[0, 0.2)$ is a "forbidden zone" (no point can be the first point here).
2. $D_2 > 0.2$: $U_{(2)}$ and $U_{(3)}$ must be at least 0.2 apart — another forbidden zone.
3. Collapse both zones: remaining interval length $= 1 - 2(0.2) = 0.6$.
4. Three points must all fall in this compressed interval: $P = 0.6^3 = 0.216$.

**Summary:** Specifying $k$ spacings "at least $m$" = removing $k$ segments of length $m$ from the interval = remaining space raised to the $n$-th power.

---

## 5. Why Normal Distribution Has No Closed Form

The derivation for Uniform relies on **exchangeability of spacings**: all $n+1$ spacings have the same joint distribution. For Normal on $(-\infty, +\infty)$:

- Points cluster near the mean (high density, small spacings) and are sparse in the tails (low density, large spacings). Spacings are **not exchangeable**.
- The support is unbounded — there is no "distance to the boundary". Only $n-1$ finite spacings exist, and their sum $X_{(n)} - X_{(1)}$ (the range) is itself random, not fixed.
- The probability integral transform $U_i = \Phi(X_i)$ maps to Uniform, but the original spacings involve $\Phi^{-1}$, which is nonlinear and destroys the closed form.

**Asymptotic result:** For any continuous density $f > 0$, the normalized maximum spacing converges to a Gumbel distribution. For Normal, the maximum spacing scales as $\sqrt{2\ln n / n}$, slower than Uniform's $\ln n / n$.

---

## 6. 1D Discrete Mesh (Bernoulli Defects)

### Setup

A one-dimensional array of $W$ nodes. Each node independently fails with probability $p$, survives with probability $q = 1-p$. Let $L_W$ be the longest consecutive run of surviving nodes.

### Exact Solution: Transfer Matrix

Track state $j$ = current run length. The transfer matrix $T$ is $s \times s$ (where $s$ is the target run length):

$$T = \begin{pmatrix} p & p & p & \cdots & p \\ q & 0 & 0 & \cdots & 0 \\ 0 & q & 0 & \cdots & 0 \\ \vdots & & \ddots & & \vdots \\ 0 & 0 & \cdots & q & 0 \end{pmatrix}$$

$$P(L_W < s) = \mathbf{1}^\top T^W \mathbf{e}_0$$

### Approximate Threshold (Erdős–Rényi Law)

A run of length $s$ is defect-free with probability $q^s$. There are $W - s + 1$ possible starting positions. At the threshold (expect exactly one such run):

$$(W - s + 1) \cdot q^s \approx 1$$

Using $\ln q = \ln(1-p) \approx -p$ and $W - s + 1 \approx W$:

$$\boxed{s^*_{1D} \approx \frac{\ln W}{p}}$$

### Correspondence: Continuous vs Discrete

| | Continuous Uniform | Discrete Bernoulli |
|---|---|---|
| Space | $[0, W]$ | $W$ lattice nodes |
| Defects | $n$ random points | $\sim \text{Binomial}(W, p)$, $E[n] = Wp$ |
| Max gap | $\frac{W \ln n}{n} \approx \frac{\ln(Wp)}{p}$ | $\frac{\ln W}{p}$ |

Both agree at leading order when $n = Wp$. The $\ln(Wp)$ vs $\ln(W)$ difference is a lower-order $\ln(p)/p$ correction.

---

# Part II — 2D Discrete Mesh: Wafer-Scale Analysis

## 7. Largest Defect-Free Square on a 2D Mesh

### Setup

A $W \times H$ mesh (wafer-scale chip). Each node independently fails with probability $p$. We seek the side length $s$ of the largest $s \times s$ fully intact sub-mesh.

### Threshold Derivation

An $s \times s$ sub-mesh is fully intact with probability:

$$q^{s^2} = (1-p)^{s^2}$$

Number of possible positions:

$$(W - s + 1)(H - s + 1)$$

Threshold condition (expect exactly one such sub-mesh):

$$(W - s + 1)(H - s + 1) \cdot q^{s^2} \approx 1$$

Taking logarithms and applying $\ln q \approx -p$, $W - s + 1 \approx W$, $H - s + 1 \approx H$:

$$\ln W + \ln H \approx p \cdot s^2$$

For a square mesh ($W = H$):

$$\boxed{s^* \approx \sqrt{\frac{2 \ln W}{p}}}$$

### 1D vs 2D Scaling

| Dimension | Max defect-free size | Scaling |
|---|---|---|
| 1D | $s^*_{1D} \approx \frac{\ln W}{p}$ | Linear in $\ln W$, inversely in $p$ |
| 2D (square) | $s^*_{2D} \approx \sqrt{\frac{2\ln W}{p}}$ | Square root of $\ln W / p$ |

Example: $W = 1000$, $p = 0.01$ gives $s^*_{1D} \approx 691$ but $s^*_{2D} \approx 37$.

---

## 8. Full Probability Distribution of the Largest Square

### Poisson Approximation

Define $N_s$ = the number of defect-free $s \times s$ sub-meshes. Its expected value:

$$\lambda(s) = (W - s + 1)(H - s + 1) \cdot (1-p)^{s^2}$$

For large meshes with small $p$, different $s \times s$ windows overlap weakly, so:

$$N_s \;\dot\sim\; \text{Poisson}(\lambda(s))$$

### CDF and PMF of the Largest Square Side $L$

$$P(L < s) = P(N_s = 0) \approx e^{-\lambda(s)}$$

$$\boxed{P(L = s) \approx e^{-\lambda(s+1)} - e^{-\lambda(s)}}$$

### Mode (Most Likely Size)

The PMF peaks where $\lambda(s)$ transitions from $\gg 1$ to $\ll 1$. This transition occurs at $\lambda(s^*) = 1$:

$$s_{\text{mode}} \approx s^* = \sqrt{\frac{2 \ln W}{p}}$$

More precisely, $s_{\text{mode}} = \lfloor s^* \rfloor$ or $\lceil s^* \rceil$.

### Standard Deviation

The rate of change of $\lambda$ at the threshold:

$$\frac{d\lambda}{ds}\bigg|_{s=s^*} \approx -2ps^*$$

The transition $\lambda \gg 1 \to \lambda \ll 1$ spans:

$$\boxed{\sigma \approx \frac{1}{2ps^*} = \frac{1}{2\sqrt{2p\ln W}}}$$

| $W$ | $p$ | $s^*$ | $\sigma$ |
|---|---|---|---|
| 100 | 0.01 | 30.3 | 1.65 |
| 500 | 0.01 | 35.2 | 1.42 |
| 1000 | 0.01 | 37.2 | 1.34 |
| 1000 | 0.005 | 52.5 | 1.90 |

**The distribution is extremely concentrated** — standard deviation of only 1–2 nodes. The largest defect-free square size is nearly deterministic.

### Physical Interpretation

The function $\lambda(s) \approx W^2 e^{-ps^2}$ exhibits a sharp cliff: it drops from astronomical values to near-zero within a narrow window around $s^*$. The PMF of $L$ is localized precisely at this cliff — the only values of $s$ where $e^{-\lambda(s+1)} - e^{-\lambda(s)}$ is appreciably nonzero. This means $s^*$ is not just an average — it is effectively a hard boundary between "abundant" and "nonexistent" defect-free sub-meshes.

---

## 9. Aspect Ratio Problem

### Unconstrained Rectangles Degenerate

If we seek the largest defect-free rectangle $s_x \times s_y$ without constraining shape, the optimal solution degenerates into an elongated strip ($1 \times A$), useless as a computational sub-mesh.

### Fixed Aspect Ratio

Constrain $s_y = \beta \cdot s_x$ for fixed $\beta > 0$:

$$(W - s_x + 1)(H - \beta s_x + 1) \cdot q^{\beta s_x^2} \approx 1$$

$$\ln W + \ln H \approx p \beta \, s_x^2$$

$$s_x^* \approx \sqrt{\frac{\ln W + \ln H}{p\beta}}, \qquad s_y^* = \beta \, s_x^*$$

### Area Is Independent of Shape

$$A^* = s_x^* \cdot s_y^* \approx \frac{\ln W + \ln H}{p}$$

The area budget is determined solely by mesh size and defect rate, **independent of $\beta$**. Without a shape constraint, the optimizer exploits this freedom to produce a useless thin strip.

### Implication for NoC Design

Any analysis of maximum usable sub-mesh must include an **aspect ratio constraint** (e.g., $\max(s_x/s_y, s_y/s_x) \leq \alpha$). The area budget $(\ln W + \ln H)/p$ is a hard limit regardless of chosen shape.

---

## 10. Approximation Validity

### Approximation 1: $\ln(1-p) \approx -p$

Taylor expansion: $\ln(1-p) = -p - p^2/2 - p^3/3 - \cdots$

| $p$ | $\ln(1-p)$ exact | $-p$ | Relative error |
|---|---|---|---|
| 0.001 | $-0.0010005$ | $-0.001$ | 0.05% |
| 0.01 | $-0.01005$ | $-0.01$ | 0.5% |
| 0.05 | $-0.05129$ | $-0.05$ | 2.5% |
| 0.10 | $-0.10536$ | $-0.10$ | 5.1% |

For wafer-scale defect rates ($p < 0.01$), the approximation is highly accurate.

### Approximation 2: $(W-s+1)^2 \approx W^2$

Relative error $\approx 2s/W$. Using $s^* = \sqrt{2\ln W / p}$:

| $W$ | $p$ | $s^*$ | $s^*/W$ | Error |
|---|---|---|---|---|
| 100 | 0.01 | 30 | 30% | Poor |
| 1000 | 0.01 | 37 | 3.7% | Acceptable |
| 1000 | 0.001 | 117 | 11.7% | Marginal |
| 10,000 | 0.01 | 43 | 0.43% | Excellent |
| 10,000 | 0.001 | 135 | 1.35% | Good |

Valid when $s^* \ll W$, i.e., $\ln W \ll pW^2/2$, satisfied for $p \gtrsim 10^{-3}$ on meshes with $W \geq 500$.

### Exact Equation (No Approximation)

$$\ln(W - s + 1) + \ln(H - s + 1) = -s^2 \ln(1-p)$$

has no closed form but is trivially solved numerically.

---

## 11. Summary

### Core Results for Wafer-Scale Design

| Quantity | Formula |
|---|---|
| Threshold (most likely size) | $s^* = \sqrt{\frac{2\ln W}{p}}$ |
| PMF | $P(L = s) \approx e^{-\lambda(s+1)} - e^{-\lambda(s)}$ |
| Expected count at size $s$ | $\lambda(s) = (W-s+1)^2(1-p)^{s^2}$ |
| Standard deviation | $\sigma \approx \frac{1}{2\sqrt{2p\ln W}}$ |
| Max defect-free area (any shape) | $A^* \approx \frac{\ln W + \ln H}{p}$ |

### Scaling Laws Across Settings

| Setting | Max defect-free size |
|---|---|
| 1D continuous, $n$ defects on $[0,1]$ | $E[M_n] \sim \frac{\ln n}{n}$ |
| 1D discrete, defect rate $p$, width $W$ | $s^* \approx \frac{\ln W}{p}$ |
| 2D discrete square, defect rate $p$, $W \times W$ | $s^* \approx \sqrt{\frac{2\ln W}{p}}$ |
| 2D discrete rectangle, aspect ratio $\beta$ | Area $\approx \frac{\ln W + \ln H}{p}$ (independent of $\beta$) |

### Design Implication

For a wafer-scale chip with mesh size $W$ and defect rate $p$, the largest usable square sub-mesh has side length $\sqrt{2\ln W / p}$ with a standard deviation of only 1–2 nodes. This value can be used directly for capacity planning. The total defect-free area budget $(\ln W + \ln H)/p$ is a hard ceiling regardless of the chosen sub-mesh shape, but an aspect ratio constraint is essential to prevent degenerate solutions.
