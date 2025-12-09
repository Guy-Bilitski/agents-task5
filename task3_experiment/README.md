# Experiment 3: RAG vs Full Context Analysis

## Overview
This experiment performs a comparative analysis between two information retrieval strategies:
1.  **Full Context (Brute Force):** Feeding the entire corpus into the LLM context window.
2.  **Retrieval-Augmented Generation (RAG):** Retrieving only relevant chunks before generation.

## Objective
Demonstrate that RAG reduces "noise" and latency while improving accuracy, especially when dealing with distractors from different semantic domains (Medicine, Law, Technology).

## Architecture
- **Data Generator:** synthetic Hebrew documents with specific domain vocabularies.
- **RAG System:** 
  - Custom TF-IDF Vector Store (No external dependencies like FAISS/Chroma required).
  - Semantic Chunking.
- **Simulation:** Mock LLM behavior modeling "Lost in the Middle" latency and noise penalties.

## Structure
- `config/`: Experiment configuration.
- `src/`: Source code.
  - `data/`: Document generation.
  - `rag/`: Indexing and Retrieval.
  - `models/`: LLM Simulation.
- `results/`: Output JSON reports.

## Running
```bash
python3 run_experiment.py
```
