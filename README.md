# LLM Context Experiments

4 experiments testing LLM behavior with varying context conditions.

## Setup
```bash
# Start Ollama
docker run -d --name ollama -p 11434:11434 ollama/ollama:latest
docker exec ollama ollama pull llama3.2:1b

# Install dependencies  
pip install pyyaml requests
```

## Experiments

### Task 1: Lost in the Middle
**Question:** Do LLMs retrieve facts better from start/end vs middle?
```bash
cd task1_experiment && python3 experiment.py
```

### Task 2: Context Window Size Impact
**Question:** How does accuracy/latency change with more documents (2→50)?
```bash
cd task2_experiment && python3 experiment.py
```

### Task 3: RAG vs Full Context
**Question:** Is RAG (retrieval) better than full context?
```bash
cd task3_experiment && python3 experiment.py
```

### Task 4: Context Management Strategies
**Question:** Which memory strategy works best for multi-step tasks?
- SELECT (RAG-based)
- COMPRESS (Summarization)
- WRITE (External memory)
```bash
cd task4_experiment && python3 experiment.py
```

## Structure
```
task{1-4}_experiment/
├── experiment.py    # Main script
├── config.yaml      # Configuration
├── utils.py         # Shared helpers
└── results/         # Output (auto-created)
```

## Output
Each experiment saves:
- `results/results_<timestamp>.json` - Full stats
- `experiment.log` - Run log
