# Experiment 3: RAG vs Full Context Analysis

## Overview
This experiment performs a comparative analysis between two information retrieval strategies:
1.  **Full Context (Brute Force):** Feeding the entire corpus into the LLM context window.
2.  **Retrieval-Augmented Generation (RAG):** Retrieving only relevant chunks before generation using **FAISS**.

## Objective
Measure and compare RAG versus full context approaches on real LLM performance (latency and accuracy), testing whether RAG mitigates "lost in the middle" effects when dealing with distractors from different semantic domains (Medicine, Law, Technology).

## Architecture
- **Data Generator:** Synthetic Hebrew documents with specific domain vocabularies.
- **RAG System (Production-Grade):**
  - **FAISS:** Facebook's similarity search library for efficient vector retrieval
  - **Sentence Transformers:** Multilingual dense embeddings (`paraphrase-multilingual-MiniLM-L12-v2`)
  - **Semantic Chunking:** Overlapping chunks for context preservation
- **Real LLM:** Ollama (llama3.2:1b) for actual latency and accuracy measurements.

## Key Features
✅ **Dense Embeddings** instead of sparse TF-IDF  
✅ **FAISS IndexFlatL2** with cosine similarity (normalized L2)  
✅ **Multilingual Support** for Hebrew documents  
✅ **Real LLM Testing** - No simulated behavior or artificial noise injection  
✅ **Industry Standard** - Production-grade RAG pipeline  

## Structure
- `config/`: Experiment configuration.
- `src/`: Source code.
  - `data/`: Document generation.
  - `rag/`: FAISS-based indexing and retrieval.
  - `evaluation/`: Metrics calculation.
- `results/`: Output JSON reports.

## Requirements
```bash
pip install -r requirements.txt
```

## Running
```bash
python3 src/run_experiment.py
```
