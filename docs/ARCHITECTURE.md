# Architecture Design Document

## LLM Context Window Experiments Platform

**Document Version:** 1.0
**Last Updated:** January 2026
**Author:** Engineering Team
**Status:** Final

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Overview](#2-system-overview)
3. [Architecture Principles](#3-architecture-principles)
4. [High-Level Architecture](#4-high-level-architecture)
5. [Component Architecture](#5-component-architecture)
6. [Data Architecture](#6-data-architecture)
7. [Plugin Architecture](#7-plugin-architecture)
8. [Sequence Diagrams](#8-sequence-diagrams)
9. [Deployment Architecture](#9-deployment-architecture)
10. [Security Architecture](#10-security-architecture)
11. [Performance Considerations](#11-performance-considerations)
12. [Technology Stack](#12-technology-stack)
13. [Design Decisions](#13-design-decisions)

---

## 1. Introduction

### 1.1 Purpose

This document describes the software architecture of the LLM Context Window Experiments Platform. It provides a comprehensive technical overview for developers, researchers, and maintainers.

### 1.2 Scope

This architecture covers:
- System components and their interactions
- Data flow and storage patterns
- Plugin and extensibility mechanisms
- Deployment and operational concerns

### 1.3 Audience

- Software Engineers implementing or extending the platform
- Research Scientists designing new experiments
- DevOps Engineers deploying and maintaining the system
- Technical Reviewers evaluating the architecture

---

## 2. System Overview

### 2.1 System Context Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL SYSTEMS                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   Ollama    │    │   OpenAI    │    │  Anthropic  │    │   HuggingF  │  │
│  │   Server    │    │    API      │    │    API      │    │    API      │  │
│  │ (localhost) │    │  (cloud)    │    │  (cloud)    │    │  (cloud)    │  │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘  │
│         │                  │                  │                  │          │
│         └──────────────────┴────────┬─────────┴──────────────────┘          │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │               LLM CONTEXT WINDOW EXPERIMENTS PLATFORM               │   │
│  │                                                                     │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐           │   │
│  │  │  Task 1   │ │  Task 2   │ │  Task 3   │ │  Task 4   │           │   │
│  │  │  Lost in  │ │  Context  │ │  RAG vs   │ │  Memory   │           │   │
│  │  │  Middle   │ │   Size    │ │  Full Ctx │ │ Strategies│           │   │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘           │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         OUTPUT ARTIFACTS                            │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐           │   │
│  │  │   JSON    │ │   Logs    │ │  Graphs   │ │  Reports  │           │   │
│  │  │  Results  │ │   Files   │ │   (PNG)   │ │   (MD)    │           │   │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 System Boundaries

| Boundary | Description | Interface |
|----------|-------------|-----------|
| LLM APIs | External language model services | HTTP/REST |
| File System | Local storage for configs and results | Python I/O |
| User Interface | Command-line interaction | stdin/stdout |

---

## 3. Architecture Principles

### 3.1 Core Principles

| Principle | Description | Implementation |
|-----------|-------------|----------------|
| **Modularity** | Components are loosely coupled and independently deployable | Plugin architecture, abstract interfaces |
| **Extensibility** | New experiments and strategies can be added without core changes | Registry pattern, base classes |
| **Reproducibility** | Same inputs produce identical outputs | Seed control, deterministic algorithms |
| **Observability** | System behavior is transparent and traceable | Structured logging, metrics collection |
| **Simplicity** | Prefer simple solutions over complex ones | Minimal dependencies, clear APIs |

### 3.2 Design Patterns Used

| Pattern | Usage | Benefit |
|---------|-------|---------|
| **Strategy** | Memory management strategies (SELECT, COMPRESS, WRITE) | Interchangeable algorithms |
| **Factory** | LLM backend creation | Decoupled instantiation |
| **Template Method** | Experiment base class | Consistent experiment structure |
| **Registry** | Plugin registration | Dynamic component discovery |
| **Observer** | Logging and metrics | Decoupled event handling |

---

## 4. High-Level Architecture

### 4.1 Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │   CLI Runner    │  │  Visualization  │  │ Report Generator│              │
│  │  (run_exp.py)   │  │ (graphs.py)     │  │  (reports.py)   │              │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘              │
└───────────┼─────────────────────┼─────────────────────┼─────────────────────┘
            │                     │                     │
            ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           APPLICATION LAYER                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      Experiment Orchestrator                         │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │    │
│  │  │ Experiment  │ │ Experiment  │ │ Experiment  │ │ Experiment  │   │    │
│  │  │   Task 1    │ │   Task 2    │ │   Task 3    │ │   Task 4    │   │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
            │                     │                     │
            ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DOMAIN LAYER                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │  Memory         │  │  RAG Pipeline   │  │  Evaluation     │              │
│  │  Strategies     │  │  (Indexer)      │  │  Metrics        │              │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘              │
│           │                    │                    │                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │  Data           │  │  Document       │  │  Statistics     │              │
│  │  Generator      │  │  Processor      │  │  Calculator     │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
└─────────────────────────────────────────────────────────────────────────────┘
            │                     │                     │
            ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INFRASTRUCTURE LAYER                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │  LLM Adapters   │  │  Configuration  │  │  Persistence    │              │
│  │  (Ollama, etc.) │  │  (YAML Parser)  │  │  (JSON, Logs)   │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │  Vector Store   │  │  Embeddings     │  │  Plugin         │              │
│  │  (FAISS)        │  │  (Sentence-Tr)  │  │  Registry       │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Component Interaction Overview

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    User      │────▶│   Config     │────▶│  Experiment  │
│   (CLI)      │     │   (YAML)     │     │   Runner     │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                     ┌────────────────────────────┼────────────────────────────┐
                     │                            │                            │
                     ▼                            ▼                            ▼
              ┌──────────────┐           ┌──────────────┐            ┌──────────────┐
              │    Data      │           │     LLM      │            │  Evaluation  │
              │  Generator   │           │   Adapter    │            │   Metrics    │
              └──────┬───────┘           └──────┬───────┘            └──────┬───────┘
                     │                          │                           │
                     ▼                          ▼                           ▼
              ┌──────────────┐           ┌──────────────┐            ┌──────────────┐
              │  Documents   │           │   Ollama     │            │  Statistics  │
              │   (Text)     │           │   Server     │            │   (NumPy)    │
              └──────────────┘           └──────────────┘            └──────────────┘
                     │                          │                           │
                     └──────────────────────────┼───────────────────────────┘
                                                │
                                                ▼
                                         ┌──────────────┐
                                         │   Results    │
                                         │ (JSON/Logs)  │
                                         └──────────────┘
```

---

## 5. Component Architecture

### 5.1 Common Module (`common/`)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              common/                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                           llm.py                                     │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │                      <<abstract>>                              │  │   │
│  │  │                        BaseLLM                                 │  │   │
│  │  │  ─────────────────────────────────────────────────────────    │  │   │
│  │  │  + generate(prompt: str) -> str                               │  │   │
│  │  │  + count_tokens(text: str) -> int                             │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  │                              △                                       │   │
│  │                              │                                       │   │
│  │              ┌───────────────┴───────────────┐                      │   │
│  │              │                               │                      │   │
│  │  ┌───────────────────────┐     ┌───────────────────────┐           │   │
│  │  │      OllamaLLM        │     │       MockLLM         │           │   │
│  │  │  ─────────────────    │     │  ─────────────────    │           │   │
│  │  │  - base_url: str      │     │  - responses: dict    │           │   │
│  │  │  - model: str         │     │  ─────────────────    │           │   │
│  │  │  - timeout: int       │     │  + generate()         │           │   │
│  │  │  ─────────────────    │     │  + count_tokens()     │           │   │
│  │  │  + generate()         │     └───────────────────────┘           │   │
│  │  │  + count_tokens()     │                                         │   │
│  │  └───────────────────────┘                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                           utils.py                                   │   │
│  │  ─────────────────────────────────────────────────────────────────  │   │
│  │  + setup_logging(name: str, log_file: Path) -> Logger               │   │
│  │  + load_config(config_path: Path) -> dict                           │   │
│  │  + save_results(results: dict, output_path: Path) -> None           │   │
│  │  + ensure_directory(path: Path) -> None                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                           data.py                                    │   │
│  │  ─────────────────────────────────────────────────────────────────  │   │
│  │  + generate_document(topic: str, length: int) -> str                │   │
│  │  + generate_needle(target: str) -> str                              │   │
│  │  + create_haystack(docs: List[str], needle: str, pos: int) -> str   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Experiment Module Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         task{N}_experiment/                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐                                                       │
│  │    config/       │                                                       │
│  │  ┌────────────┐  │                                                       │
│  │  │experiment  │  │  Configuration parameters in YAML format              │
│  │  │  .yaml     │  │  - Model settings, trial counts, thresholds          │
│  │  └────────────┘  │                                                       │
│  └──────────────────┘                                                       │
│                                                                             │
│  ┌──────────────────┐                                                       │
│  │     src/         │                                                       │
│  │  ┌────────────┐  │                                                       │
│  │  │   run_     │  │  Main experiment entry point                         │
│  │  │experiment  │  │  - Loads config, initializes components              │
│  │  │   .py      │  │  - Executes trials, collects results                 │
│  │  └────────────┘  │                                                       │
│  │  ┌────────────┐  │                                                       │
│  │  │ [domain]   │  │  Domain-specific logic (varies by task)              │
│  │  │   .py      │  │  - Task 3: rag/, evaluation/                         │
│  │  └────────────┘  │  - Task 4: agent.py, memory_strategies.py            │
│  └──────────────────┘                                                       │
│                                                                             │
│  ┌──────────────────┐                                                       │
│  │    results/      │  Experiment output directory                         │
│  │  ┌────────────┐  │  - JSON files with timestamps                        │
│  │  │results_    │  │  - Contains all metrics and raw data                 │
│  │  │<timestamp> │  │                                                       │
│  │  │  .json     │  │                                                       │
│  │  └────────────┘  │                                                       │
│  └──────────────────┘                                                       │
│                                                                             │
│  ┌──────────────────┐                                                       │
│  │     logs/        │  Structured log files                                │
│  │  ┌────────────┐  │  - INFO level logging                                │
│  │  │<exp_name>  │  │  - Timestamps, metrics, decisions                    │
│  │  │  .log      │  │                                                       │
│  │  └────────────┘  │                                                       │
│  └──────────────────┘                                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Task 3: RAG Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RAG Pipeline (Task 3)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Document Processing                           │   │
│  │                                                                      │   │
│  │   Documents      Chunking        Embedding        Indexing           │   │
│  │  ┌─────────┐   ┌─────────┐    ┌─────────┐     ┌─────────┐          │   │
│  │  │  Doc 1  │──▶│ Chunk 1 │───▶│ Vector  │────▶│         │          │   │
│  │  │  Doc 2  │   │ Chunk 2 │    │ [0.1,   │     │  FAISS  │          │   │
│  │  │  Doc 3  │   │ Chunk 3 │    │  0.5,   │     │  Index  │          │   │
│  │  │  ...    │   │ ...     │    │  ...]   │     │         │          │   │
│  │  └─────────┘   └─────────┘    └─────────┘     └─────────┘          │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                          Query Processing                            │   │
│  │                                                                      │   │
│  │    Query          Embed          Search         Retrieve             │   │
│  │  ┌─────────┐   ┌─────────┐    ┌─────────┐    ┌─────────┐           │   │
│  │  │"What is │──▶│ Query   │───▶│ k-NN    │───▶│ Top-k   │           │   │
│  │  │ the     │   │ Vector  │    │ Search  │    │ Chunks  │           │   │
│  │  │ answer?"│   │         │    │         │    │         │           │   │
│  │  └─────────┘   └─────────┘    └─────────┘    └─────────┘           │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Response Generation                          │   │
│  │                                                                      │   │
│  │   Context          Prompt           LLM           Response           │   │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐          │   │
│  │  │Retrieved│───▶│ Query + │───▶│ Ollama  │───▶│ Answer  │          │   │
│  │  │ Chunks  │    │ Context │    │ llama3  │    │         │          │   │
│  │  └─────────┘    └─────────┘    └─────────┘    └─────────┘          │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.4 Task 4: Memory Strategies Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Memory Strategies (Task 4)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      <<abstract>>                                    │   │
│  │                    BaseMemoryStrategy                                │   │
│  │  ─────────────────────────────────────────────────────────────────  │   │
│  │  + process(context: str, query: str) -> str                         │   │
│  │  + get_metrics() -> dict                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                 △                                           │
│                                 │                                           │
│         ┌───────────────────────┼───────────────────────┐                  │
│         │                       │                       │                  │
│         ▼                       ▼                       ▼                  │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐          │
│  │  SelectStrategy │   │CompressStrategy │   │  WriteStrategy  │          │
│  │  ───────────────│   │  ───────────────│   │  ───────────────│          │
│  │  RAG-based      │   │  Summarization  │   │  Scratchpad     │          │
│  │  retrieval of   │   │  of context to  │   │  persistence    │          │
│  │  relevant parts │   │  reduce tokens  │   │  across steps   │          │
│  └─────────────────┘   └─────────────────┘   └─────────────────┘          │
│         │                       │                       │                  │
│         ▼                       ▼                       ▼                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │   Input: "Step 5: What was mentioned in step 2?"                    │   │
│  │                                                                      │   │
│  │   SELECT:   Retrieves step 2 from history via similarity search     │   │
│  │   COMPRESS: Summarizes steps 1-4, appends step 5                    │   │
│  │   WRITE:    Reads from scratchpad, updates with new info            │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Data Architecture

### 6.1 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐                                                          │
│  │   Config     │                                                          │
│  │   (YAML)     │                                                          │
│  └──────┬───────┘                                                          │
│         │ load_config()                                                    │
│         ▼                                                                  │
│  ┌──────────────┐     generate_documents()      ┌──────────────┐          │
│  │  Experiment  │─────────────────────────────▶│   Synthetic   │          │
│  │   Runner     │                               │   Documents   │          │
│  └──────┬───────┘                               └──────┬───────┘          │
│         │                                              │                   │
│         │ create_prompt()                              │ embed()           │
│         ▼                                              ▼                   │
│  ┌──────────────┐                               ┌──────────────┐          │
│  │    Prompt    │                               │   Vector     │          │
│  │   (String)   │                               │   Index      │          │
│  └──────┬───────┘                               └──────┬───────┘          │
│         │                                              │                   │
│         │ generate()                                   │ search()          │
│         ▼                                              ▼                   │
│  ┌──────────────┐                               ┌──────────────┐          │
│  │     LLM      │◀─────────────────────────────│  Retrieved    │          │
│  │   Response   │      augment_context()        │   Context     │          │
│  └──────┬───────┘                               └──────────────┘          │
│         │                                                                  │
│         │ evaluate()                                                       │
│         ▼                                                                  │
│  ┌──────────────┐      save_results()           ┌──────────────┐          │
│  │   Metrics    │─────────────────────────────▶│    JSON      │          │
│  │   (dict)     │                               │   Results    │          │
│  └──────────────┘                               └──────────────┘          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Data Models

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA MODELS                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ExperimentConfig                     ExperimentResult                      │
│  ┌─────────────────────────┐         ┌─────────────────────────┐           │
│  │ + experiment_name: str  │         │ + timestamp: datetime   │           │
│  │ + model_name: str       │         │ + config: dict          │           │
│  │ + num_trials: int       │         │ + trials: List[Trial]   │           │
│  │ + seed: int             │         │ + summary: Summary      │           │
│  │ + parameters: dict      │         │ + metadata: dict        │           │
│  └─────────────────────────┘         └─────────────────────────┘           │
│                                                                             │
│  Trial                                Summary                               │
│  ┌─────────────────────────┐         ┌─────────────────────────┐           │
│  │ + trial_id: int         │         │ + accuracy_mean: float  │           │
│  │ + input: str            │         │ + accuracy_std: float   │           │
│  │ + output: str           │         │ + latency_mean: float   │           │
│  │ + expected: str         │         │ + latency_std: float    │           │
│  │ + correct: bool         │         │ + total_tokens: int     │           │
│  │ + latency_ms: float     │         │ + success_rate: float   │           │
│  │ + tokens_used: int      │         └─────────────────────────┘           │
│  └─────────────────────────┘                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.3 Storage Schema

```
project_root/
├── task{N}_experiment/
│   ├── results/
│   │   └── results_{timestamp}.json    # Experiment results
│   │       {
│   │         "timestamp": "2026-01-17T10:30:00",
│   │         "experiment": "lost_in_middle",
│   │         "config": { ... },
│   │         "trials": [ ... ],
│   │         "summary": {
│   │           "accuracy": { "mean": 0.85, "std": 0.05 },
│   │           "latency": { "mean": 1250, "std": 150 }
│   │         }
│   │       }
│   └── logs/
│       └── {experiment_name}.log       # Structured logs
│           2026-01-17 10:30:00 INFO Starting experiment...
│           2026-01-17 10:30:05 INFO Trial 1: accuracy=0.9
```

---

## 7. Plugin Architecture

### 7.1 Plugin System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PLUGIN ARCHITECTURE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Plugin Registry                               │   │
│  │  ───────────────────────────────────────────────────────────────    │   │
│  │  + register(name: str, plugin_class: Type) -> None                  │   │
│  │  + get(name: str) -> Type                                           │   │
│  │  + list_plugins() -> List[str]                                      │   │
│  │  + discover_plugins(path: Path) -> None                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                     │                                       │
│         ┌───────────────────────────┼───────────────────────────┐          │
│         │                           │                           │          │
│         ▼                           ▼                           ▼          │
│  ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐   │
│  │   LLM Plugins   │       │Strategy Plugins │       │ Metric Plugins  │   │
│  │  ─────────────  │       │  ─────────────  │       │  ─────────────  │   │
│  │  - OllamaLLM    │       │  - SelectStrat  │       │  - Accuracy     │   │
│  │  - OpenAILLM    │       │  - CompressStr  │       │  - Latency      │   │
│  │  - AnthropicLLM │       │  - WriteStrat   │       │  - TokenCount   │   │
│  │  - CustomLLM    │       │  - CustomStrat  │       │  - CustomMetric │   │
│  └─────────────────┘       └─────────────────┘       └─────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Plugin Extension Points

| Extension Point | Interface | Registration |
|-----------------|-----------|--------------|
| LLM Backend | `BaseLLM.generate()` | `llm_registry.register()` |
| Memory Strategy | `BaseStrategy.process()` | `strategy_registry.register()` |
| Evaluation Metric | `BaseMetric.compute()` | `metric_registry.register()` |
| Experiment Type | `BaseExperiment.run()` | `experiment_registry.register()` |

### 7.3 Plugin Discovery Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Startup    │────▶│    Scan      │────▶│   Validate   │────▶│   Register   │
│              │     │  plugins/    │     │  Interface   │     │  to Registry │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                            │                    │                     │
                            ▼                    ▼                     ▼
                     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
                     │  Find *.py   │     │ Check base   │     │ Available    │
                     │  files with  │     │ class impl   │     │ via config   │
                     │  @plugin     │     │ & methods    │     │ name ref     │
                     └──────────────┘     └──────────────┘     └──────────────┘
```

---

## 8. Sequence Diagrams

### 8.1 Experiment Execution Flow

```
┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐
│  User  │     │ Runner │     │ Config │     │  LLM   │     │Results │
└───┬────┘     └───┬────┘     └───┬────┘     └───┬────┘     └───┬────┘
    │              │              │              │              │
    │ python run_experiment.py    │              │              │
    │─────────────▶│              │              │              │
    │              │              │              │              │
    │              │ load_config()│              │              │
    │              │─────────────▶│              │              │
    │              │              │              │              │
    │              │    config    │              │              │
    │              │◀─────────────│              │              │
    │              │              │              │              │
    │              │──────────────────────────────────────────┐ │
    │              │         for each trial                   │ │
    │              │──────────────────────────────────────────┘ │
    │              │              │              │              │
    │              │    generate(prompt)         │              │
    │              │─────────────────────────────▶              │
    │              │              │              │              │
    │              │         response            │              │
    │              │◀─────────────────────────────              │
    │              │              │              │              │
    │              │              │    evaluate + collect       │
    │              │─────────────────────────────────────────┐ │
    │              │◀────────────────────────────────────────┘ │
    │              │              │              │              │
    │              │──────────────────────────────────────────┘ │
    │              │              │              │              │
    │              │              │    save_results()          │
    │              │─────────────────────────────────────────▶│
    │              │              │              │              │
    │   "Experiment complete"     │              │              │
    │◀─────────────│              │              │              │
    │              │              │              │              │
```

### 8.2 RAG Query Flow (Task 3)

```
┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐
│ Query  │     │Embedder│     │ FAISS  │     │  LLM   │     │Response│
└───┬────┘     └───┬────┘     └───┬────┘     └───┬────┘     └───┬────┘
    │              │              │              │              │
    │  "What is X?"│              │              │              │
    │─────────────▶│              │              │              │
    │              │              │              │              │
    │              │ encode(query)│              │              │
    │              │────────────┐ │              │              │
    │              │◀───────────┘ │              │              │
    │              │              │              │              │
    │              │ query_vector │              │              │
    │              │─────────────▶│              │              │
    │              │              │              │              │
    │              │  search(k=3) │              │              │
    │              │              │────────────┐ │              │
    │              │              │◀───────────┘ │              │
    │              │              │              │              │
    │              │ top_k_chunks │              │              │
    │◀─────────────│──────────────│              │              │
    │              │              │              │              │
    │     context + query         │              │              │
    │─────────────────────────────────────────▶│              │
    │              │              │              │              │
    │              │              │   generate() │              │
    │              │              │              │────────────┐ │
    │              │              │              │◀───────────┘ │
    │              │              │              │              │
    │                         answer             │              │
    │◀────────────────────────────────────────────────────────│
    │              │              │              │              │
```

---

## 9. Deployment Architecture

### 9.1 Local Development Setup

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LOCAL DEVELOPMENT                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Developer Machine                               │   │
│  │                                                                      │   │
│  │  ┌─────────────────┐     ┌─────────────────┐                        │   │
│  │  │   Python 3.10+  │     │    Ollama       │                        │   │
│  │  │   Virtual Env   │     │    Server       │                        │   │
│  │  │                 │     │                 │                        │   │
│  │  │  ┌───────────┐  │     │  ┌───────────┐  │                        │   │
│  │  │  │Experiments│  │────▶│  │llama3.2:1b│  │                        │   │
│  │  │  └───────────┘  │     │  └───────────┘  │                        │   │
│  │  │                 │     │                 │                        │   │
│  │  │  localhost:*    │     │ localhost:11434 │                        │   │
│  │  └─────────────────┘     └─────────────────┘                        │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                    File System                               │    │   │
│  │  │  /project                                                    │    │   │
│  │  │    ├── common/           (shared code)                       │    │   │
│  │  │    ├── task*_experiment/ (experiments)                       │    │   │
│  │  │    ├── results/          (outputs)                           │    │   │
│  │  │    └── logs/             (logs)                              │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 CI/CD Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CI/CD PIPELINE                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐          │
│  │   Push   │────▶│  Lint    │────▶│   Test   │────▶│  Report  │          │
│  │  to Git  │     │  Check   │     │   Suite  │     │ Coverage │          │
│  └──────────┘     └──────────┘     └──────────┘     └──────────┘          │
│       │                │                │                │                 │
│       │                ▼                ▼                ▼                 │
│       │         ┌──────────┐     ┌──────────┐     ┌──────────┐           │
│       │         │  flake8  │     │  pytest  │     │  codecov │           │
│       │         │  black   │     │  + mock  │     │  badge   │           │
│       │         │  mypy    │     │  LLM     │     │          │           │
│       │         └──────────┘     └──────────┘     └──────────┘           │
│       │                                                                    │
│       ▼                                                                    │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │                        GitHub Actions Workflow                        │ │
│  │                                                                       │ │
│  │  jobs:                                                                │ │
│  │    lint:        flake8, black --check, mypy                          │ │
│  │    test:        pytest --cov (with MockLLM)                          │ │
│  │    report:      upload coverage to codecov                           │ │
│  │                                                                       │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Security Architecture

### 10.1 Security Boundaries

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SECURITY ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      TRUST BOUNDARY                                  │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                    Local System                              │    │   │
│  │  │                                                              │    │   │
│  │  │  ┌─────────────┐         ┌─────────────┐                    │    │   │
│  │  │  │ Experiments │◀───────▶│   Ollama    │                    │    │   │
│  │  │  │  (Python)   │  HTTP   │  (Local)    │                    │    │   │
│  │  │  └─────────────┘         └─────────────┘                    │    │   │
│  │  │         │                                                    │    │   │
│  │  │         ▼                                                    │    │   │
│  │  │  ┌─────────────┐                                            │    │   │
│  │  │  │  Results    │  No sensitive data                         │    │   │
│  │  │  │  (JSON)     │  No external transmission                  │    │   │
│  │  │  └─────────────┘                                            │    │   │
│  │  │                                                              │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                                                                      │   │
│  │  Security Properties:                                                │   │
│  │  - All data remains local                                           │   │
│  │  - No authentication required (local Ollama)                        │   │
│  │  - No network exposure beyond localhost                             │   │
│  │  - No secrets in configuration files                                │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 10.2 Security Controls

| Control | Implementation | Status |
|---------|----------------|--------|
| Input Validation | Config schema validation | Implemented |
| No Secrets in Code | Environment variables for API keys | Implemented |
| Local-only Operation | Default to localhost:11434 | Implemented |
| Dependency Scanning | dependabot alerts | Configured |

---

## 11. Performance Considerations

### 11.1 Performance Characteristics

| Component | Bottleneck | Mitigation |
|-----------|------------|------------|
| LLM Inference | Network latency + generation time | Timeout handling, caching |
| FAISS Indexing | Memory for large document sets | Incremental indexing |
| Embedding Generation | CPU/GPU computation | Batch processing |
| Result Persistence | Disk I/O | Async writing |

### 11.2 Scalability Limits

| Resource | Limit | Recommendation |
|----------|-------|----------------|
| Documents | ~1000 per experiment | Chunk large datasets |
| Context Size | Model-dependent (4K-128K) | Configure appropriately |
| Memory | 4-8 GB typical | Monitor with large contexts |
| Disk | ~100 MB per experiment | Cleanup old results |

---

## 12. Technology Stack

### 12.1 Core Technologies

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| Runtime | Python | 3.10+ | Primary language |
| LLM | Ollama | 0.1+ | Local LLM inference |
| Vectors | FAISS | 1.7+ | Similarity search |
| Embeddings | sentence-transformers | 2.0+ | Text embeddings |
| Config | PyYAML | 6.0+ | Configuration parsing |
| HTTP | requests | 2.28+ | API communication |
| Math | NumPy | 1.24+ | Statistical computations |
| Visualization | Matplotlib | 3.7+ | Graph generation |

### 12.2 Development Tools

| Tool | Purpose | Configuration |
|------|---------|---------------|
| pytest | Testing framework | pytest.ini |
| flake8 | Linting | .flake8 |
| black | Code formatting | pyproject.toml |
| mypy | Type checking | mypy.ini |
| pre-commit | Git hooks | .pre-commit-config.yaml |

---

## 13. Design Decisions

### 13.1 Architecture Decision Records (ADRs)

#### ADR-001: Local-First LLM Integration

**Status:** Accepted

**Context:** Need to support LLM inference for experiments without requiring cloud API access.

**Decision:** Use Ollama as the primary LLM backend with localhost communication.

**Consequences:**
- (+) No API costs during development
- (+) Full reproducibility with local models
- (+) No network dependency for basic operation
- (-) Limited to Ollama-supported models
- (-) Requires local GPU/CPU resources

#### ADR-002: Plugin-Based Extensibility

**Status:** Accepted

**Context:** Researchers need to add custom experiments, strategies, and metrics without modifying core code.

**Decision:** Implement a registry-based plugin system with abstract base classes.

**Consequences:**
- (+) Easy extension without core changes
- (+) Clear interfaces for customization
- (+) Dynamic discovery of plugins
- (-) Slight complexity increase
- (-) Plugin compatibility maintenance

#### ADR-003: YAML Configuration

**Status:** Accepted

**Context:** Experiments require flexible, human-readable configuration.

**Decision:** Use YAML files for all experiment configuration.

**Consequences:**
- (+) Human-readable and editable
- (+) Support for complex nested structures
- (+) Standard format with good tooling
- (-) No schema validation by default
- (-) Whitespace sensitivity

#### ADR-004: JSON Results Storage

**Status:** Accepted

**Context:** Experiment results need to be machine-readable and archivable.

**Decision:** Store all results in timestamped JSON files.

**Consequences:**
- (+) Universal format, easy parsing
- (+) Human-readable for debugging
- (+) Easy to aggregate across runs
- (-) No query capability (vs. database)
- (-) File proliferation over time

---

## Appendix A: File Structure Reference

```
agents-task5/
├── docs/                           # Documentation
│   ├── ARCHITECTURE.md            # This document
│   ├── PRODUCT_REQUIREMENTS.md    # PRD
│   └── BUDGET_TRACKING.md         # Cost analysis
├── common/                         # Shared components
│   ├── __init__.py
│   ├── llm.py                     # LLM abstractions
│   ├── utils.py                   # Utilities
│   ├── data.py                    # Data generation
│   └── plugins.py                 # Plugin registry
├── plugins/                        # Plugin directory
│   ├── llm/                       # LLM plugins
│   ├── strategies/                # Strategy plugins
│   └── metrics/                   # Metric plugins
├── task1_experiment/              # Lost in the Middle
├── task2_experiment/              # Context Window Size
├── task3_experiment/              # RAG vs Full Context
├── task4_experiment/              # Memory Strategies
├── tests/                         # Test suite
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── conftest.py               # Pytest fixtures
├── .github/
│   └── workflows/                 # CI/CD pipelines
├── .pre-commit-config.yaml        # Pre-commit hooks
├── pyproject.toml                 # Project configuration
├── requirements.txt               # Dependencies
└── README.md                      # Project overview
```

---

**Document Revision History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Jan 2026 | Engineering Team | Initial architecture document |
