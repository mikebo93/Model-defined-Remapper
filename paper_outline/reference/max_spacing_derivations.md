# Maximum Spacing Distribution: From Continuous 1D to Discrete 2D Mesh

## Table of Contents

1. [1D Continuous: Single Point](#1-1d-continuous-single-point)
2. [1D Continuous: $n$ Points (Inclusion-Exclusion)](#2-1d-continuous-n-points)
3. [Proof of Inclusion-Exclusion Principle](#3-proof-of-inclusion-exclusion-principle)
4. [Why the Compression Argument Works](#4-why-the-compression-argument-works)
5. [Normal Distribution: No Closed Form](#5-normal-distribution-no-closed-form)
6. [1D Discrete Mesh (Bernoulli Defects)](#6-1d-discrete-mesh)
7. [2D Discrete Mesh (Largest Defect-Free Square)](#7-2d-discrete-mesh)
8. [Aspect Ratio Problem in 2D](#8-aspect-ratio-problem-in-2d)
9. [Approximation Validity](#9-approximation-validity)
10. [Summary Table](#10-summary-table)

---

## 1. 1D Continuous: Single Point

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

**Intuition:** The original $X$ is uniform on $[0,1]$. Taking $\max(X, 1-X)$ "folds" the interval at $1/2$, mapping $[0, 1/2)$ onto $(1/2, 1]$. The density doubles (from 1 to 2) and the domain halves (from length 1 to 1/2).

---

## 2. 1D Continuous: $n$ Points

### Setup

$n$ i.i.d. points $U_1, \ldots, U_n \sim \text{Uniform}(0,1)$. Order statistics: $U_{(1)} \leq \cdots \leq U_{(n)}$. This creates $n+1$ spacings:

$$D_0 = U_{(1)}, \quad D_i = U_{(i+1)} - U_{(i)} \text{ for } i=1,\ldots,n-1, \quad D_n = 1 - U_{(n)}$$

We want the distribution of $M_n = \max(D_0, D_1, \ldots, D_n)$.

### Derivation via Inclusion-Exclusion

Define events $A_i = \{D_i > m\}$ for $i = 0, 1, \ldots, n$.

**Goal:**

$$P(M_n \leq m) = P(\text{all spacings} \leq m) = 1 - P\!\left(\bigcup_{i=0}^{n} A_i\right)$$

**Key fact (compression argument — see Section 4):** Any $k$ specified spacings simultaneously exceeding $m$ has probability:

$$P(A_{i_1} \cap \cdots \cap A_{i_k}) = (1 - km)^n$$

This is the same regardless of *which* $k$ spacings are chosen (by the exchangeability of spacings). There are $\binom{n+1}{k}$ ways to choose $k$ spacings from $n+1$.

**Applying inclusion-exclusion (see Section 3):**

$$P\!\left(\bigcup_{i=0}^{n} A_i\right) = \sum_{k=1}^{n+1} (-1)^{k+1} \binom{n+1}{k}(1-km)^n$$

Therefore:

$$F_{M_n}(m) = 1 - \sum_{k=1}^{n+1} (-1)^{k+1} \binom{n+1}{k}(1-km)^n$$

Absorbing the leading 1 as the $k=0$ term (since $\binom{n+1}{0}(1-0)^n = 1$):

$$\boxed{F_{M_n}(m) = \sum_{k=0}^{\lfloor 1/m \rfloor} (-1)^k \binom{n+1}{k}(1-km)^n, \quad m \in \left[\frac{1}{n+1},\; 1\right]}$$

The upper limit $\lfloor 1/m \rfloor$ is a natural truncation: when $km > 1$, $(1-km)^n = 0$ (no interval of negative length).

### PDF

Differentiating:

$$f_{M_n}(m) = n \sum_{k=1}^{\lfloor 1/m \rfloor} (-1)^{k+1} \binom{n+1}{k}\, k\, (1-km)^{n-1}$$

### Expected Value

$$\boxed{E[M_n] = \frac{H_{n+1}}{n+1}}$$

where $H_{n+1} = \sum_{j=1}^{n+1} \frac{1}{j}$ is the harmonic number. Asymptotically, $E[M_n] \sim \frac{\ln n}{n}$.

### Support and Piecewise Structure

- **Support:** $M_n \in [1/(n+1), 1]$. The lower bound $1/(n+1)$ follows from the pigeonhole principle: $n+1$ spacings summing to 1 means the largest is at least the average.
- **Piecewise polynomial:** The inclusion-exclusion sum has $\lfloor 1/m \rfloor$ non-zero terms. As $m$ crosses each threshold $1/j$, the number of terms changes, creating a new polynomial piece. So the CDF is piecewise polynomial with breakpoints at $m = 1, 1/2, 1/3, \ldots, 1/(n+1)$.

### Verification for $n=1$

For $m \in [1/2, 1]$ (so $\lfloor 1/m \rfloor = 1$):

$$F_{M_1}(m) = \binom{2}{0}(1)^1 - \binom{2}{1}(1-m)^1 = 1 - 2(1-m) = 2m - 1$$

This is exactly $\text{Uniform}(1/2, 1)$, matching Section 1. $\checkmark$

---

## 3. Proof of Inclusion-Exclusion Principle

### Statement

For any $N$ events $A_1, \ldots, A_N$:

$$P\!\left(\bigcup_{i=1}^{N} A_i\right) = \sum_{k=1}^{N} (-1)^{k+1} \sum_{1 \leq i_1 < \cdots < i_k \leq N} P(A_{i_1} \cap \cdots \cap A_{i_k})$$

### Notation Explanation

The inner sum $\displaystyle\sum_{1 \leq i_1 < i_2 < \cdots < i_k \leq N}$ means: choose $k$ distinct indices from $\{1, 2, \ldots, N\}$ in increasing order, and sum over all such choices. The constraint $i_1 < i_2 < \cdots < i_k$ ensures each combination is counted exactly once (since $A_{i_1} \cap A_{i_2}$ and $A_{i_2} \cap A_{i_1}$ are the same event).

**Concrete example ($N=4$, fully expanded):**

- $k=1$: $\binom{4}{1} = 4$ terms — $P(A_1) + P(A_2) + P(A_3) + P(A_4)$
- $k=2$: $\binom{4}{2} = 6$ terms — $P(A_1 \cap A_2) + P(A_1 \cap A_3) + P(A_1 \cap A_4) + P(A_2 \cap A_3) + P(A_2 \cap A_4) + P(A_3 \cap A_4)$
- $k=3$: $\binom{4}{3} = 4$ terms — $P(A_1 \cap A_2 \cap A_3) + P(A_1 \cap A_2 \cap A_4) + P(A_1 \cap A_3 \cap A_4) + P(A_2 \cap A_3 \cap A_4)$
- $k=4$: $\binom{4}{4} = 1$ term — $P(A_1 \cap A_2 \cap A_3 \cap A_4)$

The full formula:

$$P\!\left(\bigcup_{i=1}^{4} A_i\right) = \underbrace{\sum_i P(A_i)}_{+4} - \underbrace{\sum_{i<j} P(A_i \cap A_j)}_{-6} + \underbrace{\sum_{i<j<l} P(A_i \cap A_j \cap A_l)}_{+4} - \underbrace{P(A_1 \cap \cdots \cap A_4)}_{-1}$$

### Proof Strategy

We show that every sample point $\omega$ in the union is counted exactly once by the right-hand side.

### Proof

Suppose $\omega$ belongs to exactly $r$ of the $N$ events ($r \geq 1$). Without loss of generality, say $\omega \in A_1, \ldots, A_r$.

At level $k$ in the sum, the intersection $A_{i_1} \cap \cdots \cap A_{i_k}$ contains $\omega$ if and only if all $k$ chosen events are among the $r$ events that contain $\omega$. The number of such intersections is $\binom{r}{k}$.

So the total count of $\omega$ is:

$$C(r) = \sum_{k=1}^{r} (-1)^{k+1} \binom{r}{k}$$

(Terms with $k > r$ contribute $\binom{r}{k} = 0$.)

**Claim:** $C(r) = 1$ for all $r \geq 1$.

**Proof of claim:** By the binomial theorem with $x = -1$:

$$(1 + (-1))^r = \sum_{k=0}^{r} \binom{r}{k}(-1)^k = 0$$

$$\binom{r}{0} + \sum_{k=1}^{r} (-1)^k \binom{r}{k} = 0$$

$$1 + \sum_{k=1}^{r} (-1)^k \binom{r}{k} = 0$$

$$\sum_{k=1}^{r} (-1)^{k+1} \binom{r}{k} = 1$$

Therefore $C(r) = 1$. Every sample point in the union is counted exactly once. $\blacksquare$

### Why $(-1)^{k+1}$ Alternates: Numerical Example

For $r = 4$ (a point belonging to 4 events):

| $k$ | Sign $(-1)^{k+1}$ | Terms $\binom{4}{k}$ | Running total |
|---|---|---|---|
| 1 | $+$ | 4 | 4 |
| 2 | $-$ | 6 | $4 - 6 = -2$ |
| 3 | $+$ | 4 | $-2 + 4 = 2$ |
| 4 | $-$ | 1 | $2 - 1 = \mathbf{1}$ |

The alternating sum always converges to 1 regardless of $r$. This is guaranteed by $(1-1)^r = 0$.

### Application to the Spacing Problem

With $N = n+1$ spacings, all $\binom{n+1}{k}$ intersection probabilities at level $k$ are equal to $(1-km)^n$. Therefore:

$$\sum_{1 \leq i_1 < \cdots < i_k \leq n+1} P(A_{i_1} \cap \cdots \cap A_{i_k}) = \binom{n+1}{k} \cdot (1-km)^n$$

This collapses the double sum into a single sum over $k$.

---

## 4. Why the Compression Argument Works

### The Claim

For $n$ uniform points on $[0,1]$, the probability that any $k$ specified spacings each exceed $m$ is $(1-km)^n$, independent of which $k$ spacings are chosen.

### Step-by-Step Proof

**Step 1: Spacings are exchangeable.**

The $n+1$ spacings $(D_0, D_1, \ldots, D_n)$ follow a symmetric Dirichlet$(1,1,\ldots,1)$ distribution, which is the uniform distribution on the $n$-simplex $\{d_i \geq 0 : \sum d_i = 1\}$. Any subset of $k$ spacings has the same joint distribution as any other subset of $k$ spacings.

**Step 2: Compression transformation.**

Require $k$ specified spacings $D_{i_1}, \ldots, D_{i_k}$ to each exceed $m$. Define new variables:

$$D'_{i_j} = D_{i_j} - m \geq 0 \quad \text{(for each of the } k \text{ specified spacings)}$$
$$D'_i = D_i \geq 0 \quad \text{(for the remaining spacings)}$$

These satisfy $\sum D'_i = 1 - km$ and are all non-negative. This is equivalent to $n$ points uniformly distributed on an interval of length $1 - km$.

**Step 3: Volume ratio.**

Under the uniform distribution on the simplex, the probability is the ratio of simplex volumes:

$$P(D_{i_1} > m, \ldots, D_{i_k} > m) = \frac{\text{Vol}((1-km)\text{-simplex})}{\text{Vol}(1\text{-simplex})} = (1-km)^n$$

The $n$-simplex $\{x_i \geq 0 : \sum x_i = L\}$ has volume proportional to $L^n$, so the ratio is $(1-km)^n / 1^n = (1-km)^n$.

### Concrete Example ($n=3$, $k=2$, $m=0.2$)

Three points create four spacings $D_0, D_1, D_2, D_3$. We want $P(D_0 > 0.2 \text{ and } D_2 > 0.2)$.

1. $D_0 > 0.2$ means the first point has at least 0.2 of empty space before it.
2. $D_2 > 0.2$ means $U_{(2)}$ and $U_{(3)}$ are at least 0.2 apart.
3. These two "forbidden zones" each lock away $m = 0.2$ of the interval.
4. Collapsing both zones: the remaining interval has length $1 - 2(0.2) = 0.6$.
5. Three points must all fall in this compressed interval: $P = 0.6^3 = 0.216$.

**One-line summary:** Specifying $k$ spacings "at least $m$" = removing $k$ segments of length $m$ from the interval = the remaining space raised to the $n$-th power.

---

## 5. Normal Distribution: No Closed Form

### Why the Uniform Result Cannot Be Extended

The entire derivation for Uniform relies on the **exchangeability of spacings**: all $n+1$ spacings have the same joint distribution, so $P(k \text{ spacings} > m)$ is the same regardless of which $k$ are chosen.

For the Normal distribution on $(-\infty, +\infty)$:

- Points cluster near the mean (high density) and are sparse in the tails (low density).
- Spacings near the center are systematically smaller than spacings in the tails.
- Spacings are **not exchangeable**, breaking the key symmetry.

Additionally, $(-\infty, +\infty)$ has no boundary, so "distance to the endpoints" is undefined. There are only $n-1$ finite spacings (between consecutive order statistics), and they do not sum to a fixed constant — their total is $X_{(n)} - X_{(1)}$ (the range), which is itself random.

### What Can Still Be Done

**Probability integral transform:** If $X_i \sim F$ (any continuous distribution), then $U_i = F(X_i) \sim \text{Uniform}(0,1)$. The Uniform spacing results apply in the $U$-space. But the original spacings are $F^{-1}(U_{(i+1)}) - F^{-1}(U_{(i)})$, and for Normal $F^{-1} = \Phi^{-1}$ (probit) is nonlinear, destroying the closed form.

**Asymptotic result:** For any continuous density $f > 0$, the maximum spacing (suitably normalized) converges to a **Gumbel distribution**:

$$P\!\left(\frac{M_n - b_n}{a_n} \leq x\right) \to e^{-e^{-x}}$$

For Normal, the maximum spacing scales as $\sqrt{2\ln n / n}$, which is slower than Uniform's $\ln n / n$ due to the tail-stretching effect of $\Phi^{-1}$.

**Monte Carlo simulation** is the practical approach for finite $n$.

---

## 6. 1D Discrete Mesh

### Setup

A one-dimensional array of $W$ nodes. Each node independently fails (defect) with probability $p$, survives with probability $q = 1-p$. Let $L_W$ be the length of the longest consecutive run of surviving nodes.

### Exact Recurrence (Transfer Matrix)

Track the state $j$ = current run length of consecutive good nodes. Define $a_j(w)$ = probability that in a length-$w$ sequence, the longest run is $< s$ and the sequence ends with exactly $j$ consecutive good nodes.

$$a_0(w) = p \sum_{j=0}^{s-1} a_j(w-1) \qquad \text{(node } w \text{ is defective, run resets)}$$

$$a_j(w) = q \cdot a_{j-1}(w-1), \quad j = 1, \ldots, s-1 \qquad \text{(run continues)}$$

Initial condition: $a_0(0) = 1$.

This can be written as a transfer matrix:

$$\mathbf{v}(w) = T \cdot \mathbf{v}(w-1), \quad T = \begin{pmatrix} p & p & p & \cdots & p \\ q & 0 & 0 & \cdots & 0 \\ 0 & q & 0 & \cdots & 0 \\ \vdots & & \ddots & & \vdots \\ 0 & 0 & \cdots & q & 0 \end{pmatrix}_{s \times s}$$

$$P(L_W < s) = \mathbf{1}^\top T^W \mathbf{e}_0$$

### Approximate Threshold (Erdős–Rényi Law)

A run of length $s$ is defect-free with probability $q^s$. There are $W - s + 1$ possible starting positions. At the critical point, expect exactly one such run:

$$(W - s + 1) \cdot q^s \approx 1$$

Taking logarithms:

$$\ln(W - s + 1) + s \ln q \approx 0$$

**Approximation 1:** $\ln q = \ln(1-p) \approx -p$ for small $p$.

This is the first-order Taylor expansion $\ln(1-p) = -p - p^2/2 - p^3/3 - \cdots$. For wafer-scale defect rates $p < 0.01$, the relative error is under 0.5%. (See Section 9 for numerical validation.)

**Approximation 2:** $W - s + 1 \approx W$ when $s \ll W$.

This gives:

$$\ln W \approx ps$$

$$\boxed{s^* \approx \frac{\ln W}{p}}$$

This is the **Erdős–Rényi law**: $L_W / \log_{1/q} W \to 1$ in probability as $W \to \infty$.

### Correspondence with Continuous Case

| | Continuous Uniform | Discrete Bernoulli |
|---|---|---|
| Space | $[0, W]$ | $W$ lattice nodes |
| Defects | $n$ random points | $\sim \text{Binomial}(W, p)$, $E[n] = Wp$ |
| Max gap | $\frac{W \ln n}{n} \approx \frac{\ln(Wp)}{p}$ | $\frac{\ln W}{p}$ |

The two results agree at leading order when $n = Wp$. The difference $\ln(Wp)$ vs $\ln(W)$ is a lower-order correction of $\ln(p)/p$.

---

## 7. 2D Discrete Mesh

### Setup

A $W \times H$ mesh. Each node independently fails with probability $p$. We seek the largest $s \times s$ defect-free sub-mesh.

### Derivation

An $s \times s$ sub-mesh is fully intact with probability:

$$q^{s^2} = (1-p)^{s^2}$$

The number of possible positions for such a sub-mesh:

$$(W - s + 1)(H - s + 1)$$

Critical condition (expect one such sub-mesh):

$$(W - s + 1)(H - s + 1) \cdot q^{s^2} \approx 1$$

Taking logarithms:

$$\ln(W - s + 1) + \ln(H - s + 1) + s^2 \ln q \approx 0$$

Applying approximations $\ln q \approx -p$ and $W - s + 1 \approx W$, $H - s + 1 \approx H$:

$$\ln W + \ln H \approx p \cdot s^2$$

For a square mesh ($W = H$):

$$\boxed{s^* \approx \sqrt{\frac{2 \ln W}{p}}}$$

### Comparison: 1D vs 2D Scaling

| Dimension | Max defect-free size | Scaling |
|---|---|---|
| 1D | $s^*_{1D} \approx \frac{\ln W}{p}$ | Linear in $\ln W$, inversely in $p$ |
| 2D (square) | $s^*_{2D} \approx \sqrt{\frac{2\ln W}{p}}$ | Square root of $\ln W / p$ |

The 2D result is much smaller because requiring $s^2$ nodes to all survive is exponentially harder than requiring $s$ nodes. For example, with $W = 1000$ and $p = 0.01$: $s^*_{1D} \approx 691$ but $s^*_{2D} \approx 37$.

---

## 8. Aspect Ratio Problem in 2D

### The Problem

The analysis above finds the largest defect-free **square**. But if we allow arbitrary rectangles $s_x \times s_y$, the optimal solution degenerates into an extremely elongated strip.

### Derivation for Fixed Aspect Ratio

Constrain $s_y = \beta \cdot s_x$ for fixed $\beta > 0$:

$$(W - s_x + 1)(H - \beta s_x + 1) \cdot q^{\beta s_x^2} \approx 1$$

$$\ln W + \ln H \approx p \beta \, s_x^2$$

$$s_x^* \approx \sqrt{\frac{\ln W + \ln H}{p\beta}}, \qquad s_y^* = \beta \, s_x^*$$

The area $A^* = s_x^* \cdot s_y^* \approx \frac{\ln W + \ln H}{p}$, which is **independent of $\beta$**.

### Why Unconstrained Rectangles Are Useless

If we maximize $s_x \cdot s_y$ without constraining the aspect ratio, the optimum pushes the shorter side toward 1 and the longer side toward $A$, degenerating into a $1 \times A$ strip. A strip of width 1 has no practical value as a computational sub-mesh in a NoC.

### Implication for NoC Design

Any analysis of maximum usable sub-mesh on a wafer-scale chip must include an **aspect ratio constraint** (e.g., $\max(s_x/s_y, s_y/s_x) \leq \alpha$). The pure "largest empty rectangle" result is misleading without this constraint. The area budget $\frac{\ln W + \ln H}{p}$ is a hard limit regardless of the chosen shape.

---

## 9. Approximation Validity

### Approximation 1: $\ln(1-p) \approx -p$

Taylor expansion: $\ln(1-p) = -p - p^2/2 - p^3/3 - \cdots$

| $p$ | $\ln(1-p)$ exact | $-p$ | Relative error |
|---|---|---|---|
| 0.001 | $-0.0010005$ | $-0.001$ | 0.05% |
| 0.01 | $-0.01005$ | $-0.01$ | 0.5% |
| 0.05 | $-0.05129$ | $-0.05$ | 2.5% |
| 0.10 | $-0.10536$ | $-0.10$ | 5.1% |

For wafer-scale defect rates ($p < 0.01$), this approximation is highly accurate.

### Approximation 2: $(W-s+1)^2 \approx W^2$

The relative error is approximately $2s/W$. Using $s^* \approx \sqrt{2\ln W / p}$:

| $W$ | $p$ | $s^*$ | $s^*/W$ | Approx. error |
|---|---|---|---|---|
| 100 | 0.01 | 30 | 30% | Poor |
| 1000 | 0.01 | 37 | 3.7% | Acceptable |
| 1000 | 0.001 | 117 | 11.7% | Marginal |
| 10,000 | 0.01 | 43 | 0.43% | Excellent |
| 10,000 | 0.001 | 135 | 1.35% | Good |

The approximation holds when $s^* \ll W$, i.e., $\ln W \ll pW^2/2$, which is satisfied for practical defect rates $p \gtrsim 10^{-3}$ on wafer-scale meshes with $W \geq 500$.

### Without the Approximation

The exact critical equation:

$$\ln(W - s + 1) + \ln(H - s + 1) = p \cdot s^2$$

has no closed-form solution but is trivially solved numerically. For papers, one can present the approximate formula $s^* \approx \sqrt{2\ln W / p}$ with a caveat and optionally include a table comparing approximate vs numerical solutions.

---

## 10. Summary Table

| Setting | Distribution | Max defect-free size | Key formula |
|---|---|---|---|
| 1D continuous, $n$ defects | $\text{Uniform}(0,1)$ | $E[M_n] = \frac{H_{n+1}}{n+1} \sim \frac{\ln n}{n}$ | $F(m) = \sum_{k=0}^{\lfloor 1/m \rfloor} (-1)^k \binom{n+1}{k}(1-km)^n$ |
| 1D discrete, defect rate $p$ | $\text{Bernoulli}(p)$ | $s^* \approx \frac{\ln W}{p}$ | Erdős–Rényi law |
| 2D discrete square, defect rate $p$ | $\text{Bernoulli}(p)$ | $s^* \approx \sqrt{\frac{2\ln W}{p}}$ | Threshold condition |
| 2D discrete rect, aspect ratio $\beta$ | $\text{Bernoulli}(p)$ | Area $\approx \frac{\ln W + \ln H}{p}$ | Independent of $\beta$ |
| Normal distribution | $\mathcal{N}(0,1)$ | No closed form | Asymptotic: Gumbel; practical: Monte Carlo |

### Key Scaling Insight

The maximum defect-free region is always a **logarithmic factor** larger than the average spacing:

- 1D: max gap $\sim \frac{\ln n}{n}$ vs average gap $\frac{1}{n+1}$, ratio $\sim \ln n$
- 2D: max square side $\sim \sqrt{\frac{\ln W}{p}}$ vs average spacing $\frac{1}{\sqrt{p}}$, ratio $\sim \sqrt{\ln W}$

This logarithmic enhancement is universal across dimensions and distributions, and represents the fundamental limit on the largest usable sub-mesh in a wafer-scale chip with random defects.
