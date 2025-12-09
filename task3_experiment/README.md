# Experiment 3: RAG vs Full Context Analysis

## Overview
This experiment performs a comparative analysis between two information retrieval strategies:
1.  **Full Context (Brute Force):** Feeding the entire corpus into the LLM context window.
2.  **Retrieval-Augmented Generation (RAG):** Retrieving only relevant chunks before generation using **FAISS**.

## Objective
Demonstrate that RAG reduces "noise" and latency while improving accuracy, especially when dealing with distractors from different semantic domains (Medicine, Law, Technology).

## Architecture
- **Data Generator:** Synthetic Hebrew documents with specific domain vocabularies.
- **RAG System (Production-Grade):**
  - **FAISS:** Facebook's similarity search library for efficient vector retrieval
  - **Sentence Transformers:** Multilingual dense embeddings (`paraphrase-multilingual-MiniLM-L12-v2`)
  - **Semantic Chunking:** Overlapping chunks for context preservation
- **Simulation:** Mock LLM behavior modeling "Lost in the Middle" latency and noise penalties.

## Key Improvements
✅ **Dense Embeddings** instead of sparse TF-IDF  
✅ **FAISS IndexFlatL2** with cosine similarity (normalized L2)  
✅ **Multilingual Support** for Hebrew documents  
✅ **Industry Standard** - No custom wheel reinvention  

## Structure
- `config/`: Experiment configuration.
- `src/`: Source code.
  - `data/`: Document generation.
  - `rag/`: FAISS-based indexing and retrieval.
  - `models/`: LLM Simulation.
- `results/`: Output JSON reports.

## Requirements
```bash
pip install -r requirements.txt
```

## Running
```bash
python3 run_experiment.py
```
