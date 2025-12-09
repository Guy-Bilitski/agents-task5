# Experiment 2: Context Window Impact

## Overview
This experiment evaluates the relationship between **Context Window Size** (number of documents/tokens) and model performance (Latency and Accuracy).

## Objective
To simulate and measure how latency increases linearly (or super-linearly) and accuracy degrades as the context size grows (e.g., from 2 to 50 documents).

## Architecture
-   **Data Generator:** Creates synthetic documents of fixed length.
-   **Scaling:** Tests at 2, 5, 10, 20, and 50 document levels.
-   **Mock Model:** Simulates latency based on token count and probabilistic failure at high loads ("Lost in the Middle" effect).

## Running
```bash
python3 src/run_experiment.py
```
