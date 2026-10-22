# Mathematical Formulation of the BNS Prediction & Safety Engine

This document establishes the formal mathematical foundations of the Bandhoo system. Every definition, variable, threshold, and objective function directly formalises the verified algorithms implemented in the codebase.

---

## 1. Mathematical Nomenclature & Symbols

| Symbol | Mathematical Domain | Description | Source File Reference |
| :--- | :--- | :--- | :--- |
| $\mathcal{C}$ | Set of documents | Verified statutory corpus containing $|\mathcal{C}| = 358$ BNS sections | [legal_engine/corpus.py](file:///c:/Users/nitaa/Downloads/Bandhu/legal_engine/corpus.py) |
| $D_j \in \mathcal{C}$ | Text document | Statutory text, title, chapter, and keywords of section $j$ | [legal_engine/corpus.py](file:///c:/Users/nitaa/Downloads/Bandhu/legal_engine/corpus.py) |
| $x \in \mathcal{V}^*$ | Character string | Raw citizen narrative complaint text ($5 \le |x| \le 8000$) | [legal_engine/service.py](file:///c:/Users/nitaa/Downloads/Bandhu/legal_engine/service.py) |
| $q \in \mathcal{V}^*$ | Sequence of tokens | Standardized query after synonym translation: $q = (t_1, \dots, t_m)$ | [legal_engine/retrieval.py](file:///c:/Users/nitaa/Downloads/Bandhu/legal_engine/retrieval.py) |
| $k_1 \in \mathbb{R}^+$ | Scalar ($1.5$) | Okapi BM25 term frequency saturation parameter | [legal_engine/retrieval.py](file:///c:/Users/nitaa/Downloads/Bandhu/legal_engine/retrieval.py) |
| $b \in [0, 1]$ | Scalar ($0.75$) | Okapi BM25 document length normalization parameter | [legal_engine/retrieval.py](file:///c:/Users/nitaa/Downloads/Bandhu/legal_engine/retrieval.py) |
| $\tau_{\text{rel}} \in [0, 1]$ | Scalar ($0.35$) | Relative candidate score pruning threshold | [legal_engine/retrieval.py](file:///c:/Users/nitaa/Downloads/Bandhu/legal_engine/retrieval.py) |
| $\sigma_{\text{floor}} \in \mathbb{R}$ | Scalar ($0.0001$) | Minimum non-zero raw BM25 score floor | [legal_engine/retrieval.py](file:///c:/Users/nitaa/Downloads/Bandhu/legal_engine/retrieval.py) |
| $\tilde{s}_j \in [0, 1]$ | Scalar | Normalized lexical relevance score of section $j$ relative to top hit | [legal_engine/retrieval.py](file:///c:/Users/nitaa/Downloads/Bandhu/legal_engine/retrieval.py) |
| $a_j \in [0, 1]$ | Scalar | LLM-assigned statutory applicability score for section $j$ | [legal_engine/service.py](file:///c:/Users/nitaa/Downloads/Bandhu/legal_engine/service.py) |
| $S_{\text{final}}(j)$ | Scalar $\in [0, 1]$ | Decoupled hybrid legal prediction score for section $j$ | [legal_engine/service.py](file:///c:/Users/nitaa/Downloads/Bandhu/legal_engine/service.py) |
| $\chi_j \in \{0, 1\}$ | Binary indicator | Statutory contradiction flag ($\chi_j = 1$ forces $S_{\text{final}} = 0$) | [legal_engine/service.py](file:///c:/Users/nitaa/Downloads/Bandhu/legal_engine/service.py) |
| $p = (\lambda, \phi)$ | Coordinate pair | Longitude ($\lambda$) and Latitude ($\phi$) in WGS84 CRS | [complaint_engine/jurisdiction.py](file:///c:/Users/nitaa/Downloads/Bandhu/complaint_engine/jurisdiction.py) |
| $\mathcal{P}_k$ | 2D Polygon Set | Geographic boundary of police station $k$ with exterior and interior rings | [complaint_engine/jurisdiction.py](file:///c:/Users/nitaa/Downloads/Bandhu/complaint_engine/jurisdiction.py) |
| $d_{\min} \in \mathbb{R}^+$ | Metric distance (m) | Shortest distance from point $p$ to any edge of polygon $\mathcal{P}_k$ | [complaint_engine/jurisdiction.py](file:///c:/Users/nitaa/Downloads/Bandhu/complaint_engine/jurisdiction.py) |
| $\theta_d \in \mathbb{R}^+$ | Scalar ($100.0\text{ m}$) | Jurisdictional boundary ambiguity safety threshold | [complaint_engine/jurisdiction.py](file:///c:/Users/nitaa/Downloads/Bandhu/complaint_engine/jurisdiction.py) |
| $\mathbf{g} \in \{0, 1\}^8$ | Binary vector | Safety audit gate vector for human-review routing | [complaint_engine/graph.py](file:///c:/Users/nitaa/Downloads/Bandhu/complaint_engine/graph.py) |

> [!IMPORTANT]
> **Scoring Ontology Note**:
> The values $\tilde{s}_j$, $a_j$, and $S_{\text{final}}(j)$ are **lexical relevance and heuristic applicability scores**, **not** calibrated frequentist or Bayesian probabilities $P(Y = j \mid x)$. The system implements no parametric statistical learning or logistic regression classifiers. Calling BM25 scores or weighted heuristic sums "probabilities" is mathematically incorrect and strictly avoided.

---

## 2. Statutory Retrieval as a Dynamic Relative-Threshold Ranking Problem

Let $\mathcal{C} = \{D_1, D_2, \dots, D_N\}$ denote the statutory corpus of $N = 358$ legal sections. Each section document $D_j$ is tokenized into a sequence of alphanumeric tokens:

$$\text{Tokens}(D_j) = \{w_{j, 1}, w_{j, 2}, \dots, w_{j, |D_j|}\}, \quad w \in \mathcal{V}, \; |w| \ge 2$$

The average document length across the statutory corpus is:

$$\text{avgdl} = \frac{1}{|\mathcal{C}|} \sum_{j=1}^{|\mathcal{C}|} |D_j|$$

### 2.1 Okapi BM25 Lexical Ranking Function
Given a query $q = (t_1, t_2, \dots, t_m)$ derived from the incident narrative, the raw lexical relevance score for document $D_j$ is defined by the Okapi BM25 formula:

$$\text{BM25}(D_j, q) = \sum_{i=1}^m \text{IDF}(t_i) \cdot \frac{f(t_i, D_j) \cdot (k_1 + 1)}{f(t_i, D_j) + k_1 \cdot \left(1 - b + b \cdot \frac{|D_j|}{\text{avgdl}}\right)}$$

where:
- $f(t_i, D_j)$ is the term frequency of token $t_i$ in statutory document $D_j$.
- $k_1 = 1.5$ controls the term frequency non-linear saturation limit.
- $b = 0.75$ controls the magnitude of document length penalisation.
- The smoothed inverse document frequency $\text{IDF}(t_i)$ is computed across the corpus $\mathcal{C}$ with floor epsilon $\epsilon = 0.25$:

$$\text{IDF}(t_i) = \ln \left( \frac{|\mathcal{C}| - n(t_i) + 0.5}{n(t_i) + 0.5} + 1 \right)$$

where $n(t_i) = |\{D \in \mathcal{C} : t_i \in D\}|$ is the document frequency of token $t_i$.

### 2.2 Dynamic Relative Thresholding & Noise Elimination
Conventional information retrieval pipelines truncate candidate sets using a static top-$K$ cutoff (e.g., $K=10$), forcing low-scoring irrelevant documents from the long tail into downstream LLM reasoning contexts. 

Bandhoo applies dynamic candidate pruning based on relative score degradation. Let the candidate set sorted descending by raw BM25 score be:

$$\Pi = \left( (D_{(1)}, s_{(1)}), (D_{(2)}, s_{(2)}), \dots, (D_{(N)}, s_{(N)}) \right), \quad s_{(1)} \ge s_{(2)} \ge \dots \ge s_{(N)}$$

where $s_{(1)} = \max_{j} \text{BM25}(D_j, q)$.

The dynamic selection filter $\Phi : \Pi \to \mathcal{R}$ retains document $D_{(r)}$ if and only if:

$$s_{(r)} \ge \sigma_{\text{floor}} \quad \land \quad \left( \frac{s_{(r)}}{s_{(1)}} \ge \tau_{\text{rel}} \quad \lor \quad r = 1 \right)$$

where $\sigma_{\text{floor}} = \max(\sigma_{\min}, 0.0001)$ and $\tau_{\text{rel}} = 0.35$.

The normalized lexical relevance score $\tilde{s}_{(r)} \in [0, 1]$ assigned to retained candidate $D_{(r)}$ is:

$$\tilde{s}_{(r)} = \text{round}\left( \min\left( \frac{s_{(r)}}{s_{(1)}}, 1.0 \right), 4 \right)$$

---

## 3. Clause-Level Multi-Action Decomposition and Max-Pooling

In real-world police complaints, citizens describe composite criminal incidents involving multiple distinct offences committed in temporal sequence (e.g., house trespass, robbery, followed by criminal intimidation). In global narrative queries, dominant lexical keywords (e.g., weapons, injury) suppress secondary statutory sections.

### 3.1 Segmentation Operator
Let narrative $x$ be partitioned into $M$ disjoint action clauses using the syntactic segmentation operator $\Psi(x)$:

$$\Psi(x) = \{c_1, c_2, \dots, c_M\}, \quad \text{where } \text{Words}(c_k) \ge 3$$

The segmentation operator splits on punctuation markers and multilingual coordinating conjunctions:

$$\Delta = \text{RegEx}\left( `(?:[.!?;:\n]+|,\s*(?:and|aur|lekin|while|also)\s+|\b(?:and\s+then|after\s+that|aur\s+phir|before\s+leaving|subsequently)\b)` \right)$$

### 3.2 Candidate Max-Pooling Formulation
Let $\tilde{s}_{\text{global}}(j)$ be the normalized BM25 score of section $j$ evaluated over the entire complaint $x$. For each clause $c_k \in \Psi(x)$, candidate retrieval yields clause-specific normalized score $\tilde{s}_{c_k}(j)$ evaluated with tight threshold $\tau_{\text{clause}} = 0.50$.

The aggregated statutory retrieval score $S_{\text{rag}}(j)$ is computed via element-wise max-pooling across the global text and all individual action clauses:

$$S_{\text{rag}}(j) = \max \left( \tilde{s}_{\text{global}}(j), \; \max_{k=1}^M \tilde{s}_{c_k}(j) \right)$$

The final retrieved shortlist $\mathcal{R}_{\text{cand}}$ is formed by taking the top $K_{\max} = 8$ sections sorted descending by $S_{\text{rag}}(j)$.

---

## 4. Statutory Element Validation and Decoupled Scoring

A critical vulnerability in RAG-based legal systems is keyword inflation: a citizen explicitly negating an offence (e.g., "no weapons were used, no one was hurt") will still trigger high lexical BM25 scores for violent offences like Robbery (BNS Section 309).

### 4.1 Statutory Contradiction Function
Let $\mathcal{N} = \{n_1, n_2, \dots, n_u\}$ denote explicit negative assertions detected in the narrative. For candidate section $j$, we define the statutory contradiction predicate $\chi_j(x, \mathcal{N}) \in \{0, 1\}$:

$$\chi_j(x, \mathcal{N}) = \begin{cases}
1 & \text{if } j = 309 \text{ (Robbery)} \land \neg(\text{Hurt} \lor \text{Restraint} \lor \text{InstantThreat}) \land \text{NonViolentTheft} \\
1 & \text{if } \text{ExplicitContradiction}(j, x, \mathcal{N}) == \text{True} \\
0 & \text{otherwise}
\end{cases}$$

### 4.2 Decoupled Scoring Formulation
Let $a_j \in [0, 1]$ be the statutory applicability score assigned by the semantic LLM validator (or derived from keyword overlap in deterministic fallback). The final prediction score $S_{\text{final}}(j)$ is governed by the decoupled piecewise function:

$$S_{\text{final}}(j) = \begin{cases}
0.0 & \text{if } \chi_j(x, \mathcal{N}) = 1 \\
0.0 & \text{if } \text{is\_explicit} \land a_j \le 0.0 \\
\text{round}\left( 0.7 \cdot a_j + 0.3 \cdot \min(S_{\text{rag}}(j), 1.0), \; 4 \right) & \text{otherwise}
\end{cases}$$

### 4.3 Decoupling Invariants
1. **Zero Inflation Invariant**:
   $$\chi_j(x, \mathcal{N}) = 1 \implies S_{\text{final}}(j) = 0.0 \quad (\forall S_{\text{rag}}(j) \in [0, 1])$$
   *Mathematical Proof*: If an essential statutory ingredient is contradicted by the facts, no degree of lexical similarity ($S_{\text{rag}} = 1.0$) can inflate the prediction score above zero.
2. **Dominance of Statutory Validity**:
   $$\frac{\partial S_{\text{final}}}{\partial a_j} = 0.7 > \frac{\partial S_{\text{final}}}{\partial S_{\text{rag}}} = 0.3$$
   The semantic satisfaction of statutory elements contributes more than double the weight of surface lexical similarity.

---

## 5. Fact Grounding as Exact Substring Mapping

To eliminate hallucination, fact extraction is modeled as an exact character span mapping from the complainant statement $T$.

### 5.1 Formal Definition of a Fact Item
A structured fact item $f$ is a 5-tuple:

$$f = \left( \text{id}, \; v, \; k, \; \text{prov}, \; \Sigma \right)$$

where:
- $\text{id} \in \mathbb{N}$ is a unique item identifier.
- $v \in \mathcal{V}^*$ is the factual value (e.g., `"gold chain"`, `"₹15,000"`).
- $k \in \mathcal{K}_{\text{kinds}}$ is the entity type (e.g., `datetime`, `location`, `property`, `weapon`).
- $\text{prov} \in \{\text{"complainant\_statement"}, \text{"ai\_inference"}, \text{"police\_officer"}\}$ is the provenance origin.
- $\Sigma = \{s_1, s_2, \dots, s_p\}$ is the set of character spans.

### 5.2 Exact Span Validity Predicate
Each span $s_i$ is defined by a statement identifier and boundary indices: $s_i = (\text{stmt\_id}, \text{start}, \text{end}, \text{span\_text})$. Let $T_{\text{stmt\_id}}$ be the verbatim text of the referenced statement. The span validity predicate $\mathcal{V}(s_i)$ is defined as:

$$\mathcal{V}(s_i) \iff \left( 0 \le s_i.\text{start} < s_i.\text{end} \le |T_{\text{stmt\_id}}| \right) \quad \land \quad \left( T_{\text{stmt\_id}}[s_i.\text{start} : s_i.\text{end}] \equiv s_i.\text{span\_text} \right)$$

### 5.3 Fact Acceptance Criterion
An extracted fact item $f$ is admitted into the structured legal complaint if and only if all supporting spans satisfy strict character equality:

$$\text{Admit}(f) \iff |\Sigma| \ge 1 \quad \land \quad \bigwedge_{s \in \Sigma} \mathcal{V}(s) == \text{True}$$

Any fact generated by an external LLM failing $\text{Admit}(f)$ is routed to the rejected items log $\mathcal{R}_{\text{rej}}$ and excluded from the complaint narrative.

---

## 6. Point-in-Polygon Jurisdiction Assignment & Boundary Buffer

Police station territorial allocation is modeled as a 2D point-in-polygon containment problem over geographic coordinates $p = (\lambda, \phi)$, where $\lambda$ is longitude and $\phi$ is latitude in WGS84 CRS.

### 6.1 Polygon Boundary Representation
Each police station jurisdiction $k \in \{1, \dots, K\}$ is represented by a 2D geometry $\mathcal{P}_k$:

$$\mathcal{P}_k = \left( R_{k, 0}, \; \{R_{k, 1}, R_{k, 2}, \dots, R_{k, h_k}\} \right)$$

where $R_{k, 0}$ is the exterior boundary ring of ordered vertices $((x_0, y_0), \dots, (x_n, y_n))$, and $R_{k, i}$ ($i \ge 1$) are interior hole rings.

### 6.2 Ray-Casting Containment Function
Using the Jordan curve theorem, the winding crossing function $\Omega(p, R)$ for point $p = (x, y)$ against ring $R = (v_0, \dots, v_n)$ is evaluated by counting ray intersections extending along the positive $x$-axis:

$$\Omega(p, R) = \bigoplus_{i=1}^n \left[ (v_i.y > y \neq v_{i-1}.y > y) \land \left( x < \frac{(v_{i-1}.x - v_i.x)(y - v_i.y)}{v_{i-1}.y - v_i.y} + v_i.x \right) \right]$$

where $\bigoplus$ denotes the binary XOR (odd-parity) operator.

The geometry containment predicate $\text{Inside}(p, \mathcal{P}_k)$ is:

$$\text{Inside}(p, \mathcal{P}_k) \iff \Omega(p, R_{k, 0}) == 1 \quad \land \quad \bigwedge_{i=1}^{h_k} \Omega(p, R_{k, i}) == 0$$

### 6.3 Local Equirectangular Boundary Distance Metric
For high-speed metric calculations, spherical geographic coordinates are projected into local metric space $(\tilde{x}, \tilde{y})$ centered at incident latitude $\phi$:

$$k_x = 111{,}320 \cdot \cos\left(\frac{\pi \cdot \phi}{180}\right) \text{ meters/degree}, \quad k_y = 110{,}540 \text{ meters/degree}$$

For each line segment $e = (v_1, v_2) \in \partial \mathcal{P}_k$, define relative displacement vectors:

$$\vec{a} = \left( (v_1.x - \lambda) \cdot k_x, \; (v_1.y - \phi) \cdot k_y \right)$$

$$\vec{b} = \left( (v_2.x - \lambda) \cdot k_x, \; (v_2.y - \phi) \cdot k_y \right)$$

$$\vec{d} = \vec{b} - \vec{a} = (d_x, d_y), \quad \|\vec{d}\|^2 = d_x^2 + d_y^2$$

The projection scalar $t^* \in [0, 1]$ finding the closest point on segment $e$ to origin $(0, 0)$ is:

$$t^* = \text{clamp}\left( -\frac{\vec{a} \cdot \vec{d}}{\|\vec{d}\|^2}, \; 0.0, \; 1.0 \right) = \max\left( 0.0, \; \min\left( 1.0, \; -\frac{a_x d_x + a_y d_y}{d_x^2 + d_y^2} \right) \right)$$

The minimum Euclidean distance to boundary $\partial \mathcal{P}_k$ is:

$$d_{\min}(p, \partial \mathcal{P}_k) = \min_{e \in \partial \mathcal{P}_k} \|\vec{a} + t^* \vec{d}\|_2 = \min_{e \in \partial \mathcal{P}_k} \sqrt{(a_x + t^* d_x)^2 + (a_y + t^* d_y)^2}$$

### 6.4 Jurisdictional Allocation Decision Function
Let $\mathcal{H}(p) = \{k : \text{Inside}(p, \mathcal{P}_k) == \text{True}\}$ be the set of matching station polygons. The final station assignment $\Gamma(p)$ is defined by the decision rule:

$$\Gamma(p) = \begin{cases}
(\text{"no\_location"}, \text{null}) & \text{if } p \text{ is undefined or non-finite} \\
(\text{"outside\_all"}, \text{null}) & \text{if } |\mathcal{H}(p)| = 0 \\
(\text{"multiple"}, \text{null}) & \text{if } |\mathcal{H}(p)| > 1 \\
(\text{"near\_boundary"}, \text{null}) & \text{if } |\mathcal{H}(p)| = 1 \land d_{\min}(p, \partial \mathcal{P}_{k^*}) < \theta_d \\
(\text{"inside"}, \text{Station}_{k^*}) & \text{if } |\mathcal{H}(p)| = 1 \land d_{\min}(p, \partial \mathcal{P}_{k^*}) \ge \theta_d
\end{cases}$$

where safety buffer threshold $\theta_d = 100.0\text{ meters}$.

---

## 7. Rule-Based Uncertainty and Human-Review Safety Routing

The decision to route a structured complaint to automated police draft compilation versus mandatory human officer review is formalised as a multi-criteria conjunct over an 8-dimensional binary safety gate vector $\mathbf{g} = (g_1, g_2, \dots, g_8) \in \{0, 1\}^8$.

### 7.1 Safety Gate Definitions
1. **$g_1$ (Input Integrity)**: $g_1 = 1 \iff \text{Length}(x) \ge 5 \land \text{input\_valid} == \text{True}$.
2. **$g_2$ (Cryptographic Nonce & Statement Immutability)**:
   $$g_2 = 1 \iff \text{SHA256}(T_{\text{original}}) == \text{initial\_hash}$$
3. **$g_3$ (Grounding & Provenance)**:
   $$g_3 = 1 \iff \forall f \in \mathcal{F}, \; \text{Admit}(f) == \text{True} \land |\mathcal{R}_{\text{rej}}| == 0$$
4. **$g_4$ (Internal Consistency)**:
   $$g_4 = 1 \iff |\text{Contradictions}| == 0$$
5. **$g_5$ (Unambiguous Jurisdiction)**:
   $$g_5 = 1 \iff \Gamma(p).\text{status} == \text{"inside"}$$
6. **$g_6$ (Completeness of Core Statutory Information)**:
   $$g_6 = 1 \iff \forall c \in \{\text{incident\_type}, \text{location}, \text{datetime}\}, \; c \notin \text{Missing}_{\text{open}}$$
7. **$g_7$ (High-Risk Incident Safeguard)**:
   $$g_7 = 1 \iff \text{RegExMatch}(\text{HIGH\_RISK\_PATTERNS}, x) == \text{False}$$
   (Flags weapons, serious bodily injury, sexual offences, minors, or threats to life).
8. **$g_8$ (Zero Node Pipeline Errors)**:
   $$g_8 = 1 \iff |\text{Errors}| == 0$$

### 7.2 Safety Routing Function
The operational review route $\mathcal{R}(\mathbf{g})$ is strictly conjunctive:

$$\mathcal{R}(\mathbf{g}) = \begin{cases}
\text{"ready\_for\_police\_review"} & \text{if } \sum_{i=1}^8 g_i = 8 \\
\text{"human\_review\_required"} & \text{if } \sum_{i=1}^8 g_i < 8 \land g_1 = 1 \\
\text{"review\_status\_unavailable"} & \text{if } g_1 = 0 \lor g_2 = 0
\end{cases}$$

Under this formulation, the system is fail-safe: **any single missing, uncertain, or contradictory attribute forces the complaint to human review**.

---

## 8. Evidence Quality and Duplicate Screening Metrics

Let $B$ denote the uploaded binary file buffer of length $|B|$ bytes ($|B| \le 50 \times 1024^2$).

### 8.1 Header Magic-Byte Validation
The file format is valid if and only if the prefix $B[0 : 32]$ matches verified signature bytes:

$$\text{FormatValid}(B) \iff \exists (M, \mathcal{S}) \in \text{SUPPORTED\_TYPES} : \exists s \in \mathcal{S} \text{ s.t. } s \sqsubseteq B[0 : 32]$$

### 8.2 Deterministic Byte Variance and Sharpness Metric
To screen image readability without external neural networks, a deterministic gradient heuristic is computed over a sample slice $S = B[64 : \min(|B|, 4096)]$:

$$\mu = \frac{1}{|S|} \sum_{i=1}^{|S|} S_i, \quad \Delta_{\text{avg}} = \frac{1}{|S|-1} \sum_{i=2}^{|S|} |S_i - S_{i-1}|$$

The exposure state and sharpness score $\sigma_{\text{sharp}} \in [0.05, 1.0]$ are defined by:

$$\text{Exposure}(S) = \begin{cases}
\text{"underexposed\_dark"} & \text{if } \mu < 10.0 \\
\text{"overexposed\_white"} & \text{if } \mu > 245.0 \\
\text{"normal"} & \text{otherwise}
\end{cases}$$

$$\sigma_{\text{sharp}}(S) = \begin{cases}
0.2 & \text{if } \text{Exposure}(S) \neq \text{"normal"} \\
\min\left(1.0, \; \max\left(0.05, \; \frac{\Delta_{\text{avg}}}{10.0}\right)\right) & \text{if } \text{Exposure}(S) == \text{"normal"}
\end{cases}$$

### 8.3 Duplicate Detection via Difference Hash (dHash)
For an image scaled to $9 \times 8$ grayscale matrix $G \in [0, 255]^{9 \times 8}$:

$$H_{i, j} = \begin{cases} 1 & \text{if } G_{i+1, j} > G_{i, j} \\ 0 & \text{otherwise} \end{cases}, \quad i \in \{0, \dots, 7\}, \; j \in \{0, \dots, 7\}$$

Two images with 64-bit hashes $H_1, H_2$ are flagged as duplicate uploads if their Hamming distance $D_H$ satisfies:

$$D_H(H_1, H_2) = \sum_{k=1}^{64} (H_{1, k} \oplus H_{2, k}) \le 5$$
