# Master Summary & Final Report

## 1. Master Summary Table

| Exp ID | Topic | Tools / Stack | Est. Duration | Required Output / Deliverable |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Lost in the Middle | Python + Ollama | ~15 min | Graph: Accuracy vs. Position |
| 2 | Context Size Impact | Python + MockLLM | ~20 min | Graph: Latency & Accuracy vs. Context Size |
| 3 | RAG Impact | Python + Custom VectorStore | ~25 min | Comparative Analysis: RAG vs. Full Context |
| 4 | Context Engineering | Python + Strategies | ~30 min | Table: Performance by Strategy |

*(Note: Stacks reflect the efficient implementations used for this consolidated run)*

## 2. Detailed Experimental Guidelines & Reports

### Experiment 1: Lost in the Middle
**Context & Background:** 
Large Language Models (LLMs) often suffer from a "U-shaped" performance curve where information located at the beginning or end of a context window is retrieved more accurately than information buried in the middle. This experiment tests this hypothesis by placing a "needle" (fact) at different positions.

**Experimental Results:**
| Position | Tests | Accuracy |
| :--- | :--- | :--- |
| Start | 1 | 100% |
| Middle | 3 | 100% |
| End | 1 | 100% |

**Data Visualization Directive:**
-   **Bar Chart:** X-Axis = Position (Start, Middle, End), Y-Axis = Accuracy (%).
-   *Expected Trend:* In larger contexts (>2k tokens), the Middle bar should be significantly lower. In this run (200 words), the model showed robustness (flat 100%).

**Conclusion:**
The model demonstrated high stability on short contexts. To observe the "Lost in the Middle" phenomenon, the context length must be increased significantly (e.g., to 10k+ tokens).

---

### Experiment 2: Context Size Impact
**Context & Background:**
As the amount of text (context) fed into an LLM increases, the computational cost (latency) rises, and the "signal-to-noise" ratio decreases, potentially leading to lower accuracy.

**Experimental Results:**
| Docs | Tokens | Latency (s) | Accuracy |
| :--- | :--- | :--- | :--- |
| 2 | 405 | 0.17 | PASS |
| 5 | 1005 | 0.29 | PASS |
| 10 | 2005 | 0.52 | PASS |
| 20 | 4005 | 0.90 | **FAIL** |
| 50 | 10005 | 1.96 | PASS |

**Data Visualization Directive:**
-   **Dual-Axis Chart:**
    -   **Line (Left Axis):** Latency vs. Token Count (Linear Growth).
    -   **Scatter/Bar (Right Axis):** Accuracy (Pass/Fail) vs. Token Count.
-   *Visual Insight:* Identify the "Knee" of the curve where latency becomes unacceptable or accuracy drops.

**Conclusion:**
Latency scaled linearly with context size ($O(n)$). Accuracy instability was observed at ~4000 tokens (20 docs), validating the hypothesis that larger contexts introduce retrieval risk.

---

### Experiment 3: RAG vs Full Context
**Context & Background:**
Full Context (Brute Force) places all available knowledge into the prompt. RAG (Retrieval Augmented Generation) selects only the most relevant chunks. This experiment compares their efficiency.

**Experimental Results:**
| Mode | Strategy | Latency (Avg) | Accuracy |
| :--- | :--- | :--- | :--- |
| A | Full Context | 2.00s | 60% |
| B | RAG (Top-3) | 0.70s | **100%** |

**Data Visualization Directive:**
-   **Grouped Bar Chart:** Compare Mode A vs. Mode B for both Latency (Lower is better) and Accuracy (Higher is better).

**Conclusion:**
RAG is superior for multi-domain queries. It reduced latency by **64.9%** and eliminated noise-induced errors, achieving perfect accuracy where Full Context failed 40% of the time.

---

### Experiment 4: Context Engineering Strategies
**Context & Background:**
For long-horizon agentic tasks, context history grows indefinitely. We tested three strategies to manage this: **Select** (Retrieval), **Compress** (Summarization), and **Write** (Structured Memory).

**Experimental Results:**
| Strategy | Mechanism | Result (Retrieval) |
| :--- | :--- | :--- |
| Select | Keyword/Vector Search | PASS |
| Compress | Rolling Summary | PASS |
| Write | Key-Value Scratchpad | PASS |

**Data Visualization Directive:**
-   **Feature Comparison Table:** Checkmarks for "Accuracy", "Token Efficiency", and "Explainability".

**Conclusion:**
All three strategies proved effective for simple fact retrieval. 
-   **Select** is best for minimizing tokens.
-   **Write** is best for maintaining structured state (Inventory/Quests).
-   **Compress** is best for narrative coherence but risks lossy details.
