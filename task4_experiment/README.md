# Experiment 4: Context Strategies Benchmarking

## Overview
This experiment evaluates three different strategies for managing long-horizon context in agentic tasks:
1.  **SELECT (RAG-based):** Retaining full history but retrieving only relevant parts at query time.
2.  **COMPRESS (Summarization):** Periodically summarizing older history to fit within token limits.
3.  **WRITE (Scratchpad):** Maintaining a structured external memory state updated at each step.

## Objective
To determine which strategy best maintains accuracy for specific fact retrieval ("What color was the key?") while managing token usage.

## Architecture
-   **Simulation:** A 10-step sequential action generator (finding keys, meeting NPCs).
-   **Strategies:** Implemented in `src/strategies.py`.
-   **Evaluation:** Checking if the target fact ("Blue") is present in the final context passed to the model.

## Running
```bash
python3 src/run_experiment.py
```
