# Experiment 2: Context Window Impact

## Overview
This experiment evaluates the relationship between **Context Window Size** (number of documents/tokens) and model performance (Latency and Accuracy).

## Objective
To measure how latency increases and accuracy changes as the context size grows (e.g., from 2 to 30 documents) using a real LLM via Ollama.

## Architecture
-   **Data Generator:** Creates synthetic documents of fixed length.
-   **Scaling:** Tests at 2, 5, 10, 20, and 30 document levels.
-   **Real Model:** Uses Ollama (llama3.2:1b) to measure actual latency and accuracy with increasing context sizes.

## Running
```bash
python3 src/run_experiment.py
```
