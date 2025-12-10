# LLM Context Window Experiments

A comprehensive suite of 4 experiments investigating how Large Language Models (LLMs) handle varying context conditions, information retrieval, and memory management strategies.

## 📋 Overview

This repository contains systematic experiments designed to explore critical aspects of LLM behavior:

1. **Lost in the Middle** - Positional bias in context retrieval
2. **Context Window Size Impact** - Performance scaling with context length
3. **RAG vs Full Context** - Retrieval-augmented generation efficiency
4. **Context Management Strategies** - Memory strategies for multi-step tasks

## 🚀 Quick Start

### Prerequisites

```bash
# Start Ollama (for Task 1 - real LLM testing)
docker run -d --name ollama -p 11434:11434 ollama/ollama:latest
docker exec ollama ollama pull llama3.2:1b

# Install dependencies
pip install -r requirements.txt
```

### Running Experiments

Each experiment can be run independently:

```bash
# Task 1: Lost in the Middle
cd task1_experiment && python3 src/run_experiment.py

# Task 2: Context Window Size Impact
cd task2_experiment && python3 src/run_experiment.py

# Task 3: RAG vs Full Context
cd task3_experiment && python3 src/run_experiment.py

# Task 4: Context Management Strategies
cd task4_experiment && python3 src/run_experiment.py
```

## 📂 Project Structure

```
agents-task5/
├── common/                      # Shared utilities across all experiments
│   ├── __init__.py
│   ├── utils.py                # Logging, config, I/O utilities
│   ├── llm.py                  # Mock LLM simulators
│   └── data.py                 # Text generation utilities
│
├── task1_experiment/           # Lost in the Middle
│   ├── config/
│   │   └── experiment.yaml     # Experiment configuration
│   ├── src/
│   │   └── run_experiment.py   # Main experiment script
│   ├── logs/                   # Generated logs
│   ├── results/                # JSON results
│   └── README.md               # Experiment documentation
│
├── task2_experiment/           # Context Window Size Impact
│   ├── config/
│   ├── src/
│   ├── logs/
│   ├── results/
│   └── README.md
│
├── task3_experiment/           # RAG vs Full Context
│   ├── config/
│   ├── src/
│   │   ├── data/              # Document generation
│   │   ├── rag/               # FAISS-based retrieval
│   │   ├── models/            # LLM simulation
│   │   └── evaluation/        # Metrics calculation
│   ├── logs/
│   ├── results/
│   └── README.md
│
├── task4_experiment/           # Context Management Strategies
│   ├── config/
│   ├── src/
│   │   └── strategies.py      # SELECT, COMPRESS, WRITE strategies
│   ├── logs/
│   ├── results/
│   └── README.md
│
├── requirements.txt            # Project dependencies
└── README.md                   # This file
```

## 🔬 Experiments

### Task 1: Lost in the Middle

**Research Question:** Do LLMs retrieve facts better from the start/end versus the middle of context?

**Hypothesis:** Facts at edges (start/end) are retrieved more accurately than those in the middle.

**Method:** Insert a critical fact at different positions (0%, 50%, 100%) in documents and measure retrieval accuracy.

**Expected Outcome:** Higher accuracy for start/end positions, demonstrating positional bias.

[📖 Full Documentation](task1_experiment/README.md)

---

### Task 2: Context Window Size Impact

**Research Question:** How do accuracy and latency change as context size increases from 2 to 50 documents?

**Hypothesis:** Latency increases linearly (or super-linearly) while accuracy degrades with larger contexts.

**Method:** Test model performance with varying document counts (2, 5, 10, 20, 50).

**Expected Outcome:** Demonstrate the trade-off between context size and performance.

[📖 Full Documentation](task2_experiment/README.md)

---

### Task 3: RAG vs Full Context

**Research Question:** Is Retrieval-Augmented Generation (RAG) more efficient than full context processing?

**Hypothesis:** RAG reduces latency and improves accuracy by filtering irrelevant information.

**Method:** Compare full-context vs FAISS-based RAG retrieval on multi-domain documents.

**Technology:** FAISS, Sentence Transformers, multilingual embeddings.

**Expected Outcome:** RAG demonstrates better efficiency and accuracy by reducing noise.

[📖 Full Documentation](task3_experiment/README.md)

---

### Task 4: Context Management Strategies

**Research Question:** Which memory management strategy works best for multi-step agentic tasks?

**Strategies Tested:**
- **SELECT (RAG):** Retrieve only relevant historical context
- **COMPRESS (Summarization):** Periodically summarize history to reduce tokens
- **WRITE (Scratchpad):** Maintain structured external memory

**Expected Outcome:**
- SELECT: ✅ PASS (retrieves key information)
- COMPRESS: ❌ FAIL (loses specific details in summary)
- WRITE: ✅ PASS (preserves structured facts)

[📖 Full Documentation](task4_experiment/README.md)

## 📊 Output Format

Each experiment generates:

- **Logs:** `logs/<experiment_name>.log` - Detailed execution logs
- **Results:** `results/results_<timestamp>.json` - Structured experiment data including:
  - Configuration used
  - Raw measurements
  - Statistical summaries
  - Hypothesis validation

## 🛠️ Configuration

Each experiment has a `config/experiment.yaml` file that can be customized:

- **Experiment metadata:** Name, description, seed for reproducibility
- **Model settings:** URL, name, temperature, token limits
- **Dataset parameters:** Document sizes, test cases, queries
- **Logging options:** Level, console/file output
- **Output directories:** Results and log paths

## 🧪 Testing Methodology

All experiments follow a consistent methodology:

1. **Reproducibility:** Fixed random seeds for consistent results
2. **Logging:** Comprehensive logging at INFO level
3. **Structured Output:** JSON results with timestamps
4. **Hypothesis-Driven:** Clear expected outcomes
5. **Modularity:** Shared common utilities, experiment-specific logic

## 📦 Dependencies

- **Core:** `pyyaml`, `requests`
- **Task 3 specific:** `faiss-cpu`, `sentence-transformers`, `numpy`, `torch`

See `requirements.txt` for full details.

## 📈 Expected Results Summary

| Task | Hypothesis | Expected Outcome |
|------|------------|------------------|
| 1 | Edges > Middle | Start/End accuracy > Middle accuracy |
| 2 | Size ↑ → Performance ↓ | Latency ↑, Accuracy ↓ with more docs |
| 3 | RAG > Full Context | RAG: Lower latency, higher accuracy |
| 4 | Structured memory best | SELECT ✅, COMPRESS ❌, WRITE ✅ |

## 🎯 Key Insights

- **Positional Bias:** LLMs exhibit "Lost in the Middle" phenomenon
- **Scalability Trade-offs:** Larger contexts incur latency and accuracy costs
- **RAG Efficiency:** Retrieval-based methods outperform brute-force approaches
- **Memory Strategies:** Structured external memory preserves critical information better than compression

## 📝 License

This project is created for educational and research purposes.

## 👥 Author

Created as part of LLM context window research experiments.
