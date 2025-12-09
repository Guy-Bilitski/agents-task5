# Presentation Strategy & Plan

## Objective
To convincingly demonstrate to stakeholders (or academic supervisors) that **Retrieval Augmented Generation (RAG)** and **Structured Memory** are superior strategies for handling large-context and long-horizon tasks compared to brute-force context stuffing.

## Narrative Arc
1.  **The Problem:** LLMs are powerful but have limits.
    *   *Show Task 1:* They get confused even in small contexts if information is buried ("Lost in the Middle").
    *   *Show Task 2:* As we add more data, they get slower and dumber (Linear Latency, Drop in Accuracy).
2.  **The Solution:** Smarter Context Management.
    *   *Show Task 3:* **RAG** solves the noise problem. It finds the needle instantly. compare the 60% vs 100% accuracy bars.
    *   *Show Task 4:* For long tasks, we need strategies like **Summarization** or **Scratchpads** to stay efficient.

## Slide Outline

### Slide 1: Title
*   **Title:** Optimizing LLM Retrieval & Context
*   **Subtitle:** From Brute Force to RAG & Agents
*   **Presenter:** [Student Name]

### Slide 2: The "Lost in the Middle" Phenomenon
*   **Goal:** Prove position bias exists.
*   **Visual:** `task1_accuracy.png` (Bar chart showing Start/End > Middle).
*   **Key Takeaway:** "If you bury the fact, the model misses it."

### Slide 3: The Cost of Scale
*   **Goal:** Show why we can't just "add more tokens".
*   **Visual:** `task2_impact.png` (Dual axis: Latency going UP, Accuracy going DOWN).
*   **Key Takeaway:** "20+ documents break the system."

### Slide 4: RAG to the Rescue
*   **Goal:** The hero moment. Comparison of Task 3.
*   **Visual:** `task3_comparison.png` (Side-by-side comparison).
*   **Key Stat:** "64% Faster, 100% Accurate."

### Slide 5: Long-Horizon Strategies
*   **Goal:** How to handle infinite history?
*   **Content:** Table comparing Select vs. Compress vs. Write.
*   **Conclusion:** "Structured Memory (Write) provides the best balance of state tracking and efficiency."

## Tools Provided
*   `presentation/visualize_results.py`: Run this script to generate the exact PNG charts needed for Slides 2, 3, and 4.
*   `MASTER_REPORT.md`: Contains the raw data tables.

## Final Conclusion
The experiments conclusively prove that **Context Engineering** (RAG, Filtering) is not just an optimization, but a **requirement** for reliable production AI systems.
