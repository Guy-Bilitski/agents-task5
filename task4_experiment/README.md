# Experiment 4: Memory Management Strategies for Multi-Step LLM Agents

## Overview
This experiment evaluates three memory management strategies for multi-step LLM agents:

1.  **SELECT (RAG-based):** Semantic retrieval using sentence embeddings
2.  **COMPRESS (Summarization):** LLM-based periodic summarization  
3.  **WRITE (Scratchpad):** LLM-based structured information extraction

## Objective
Measure which strategy best maintains accuracy for specific fact retrieval while managing computational costs (latency, tokens, LLM calls).

## Implementation

### Core Components
- **Agent** (`src/agent.py`): Multi-step agent with pluggable memory strategies
- **Strategies** (`src/memory_strategies.py`): SELECT, COMPRESS, WRITE implementations
- **Experiment Runner** (`src/run_experiment.py`): Main execution script with 5 trials per strategy

### Architecture

| Strategy | LLM Calls | When | Strength |
|----------|-----------|------|----------|
| SELECT | 1 | Query only | Efficiency |
| COMPRESS | 4-5 | Processing + Query | Memory-efficient |
| WRITE | 11 | Every step + Query | Accuracy |

## Scenario

**10-Step Text Adventure:**
1. Found a **Blue Key** under the mat
2. Unlocked the Oak Door
3. Saw Red Painting
4. Met Guard Steve
5. Steve asked for password
6. Found password note ("Shadow")
7. Gave password to Steve
8. Steve opened Gate
9. Entered Garden
10. Found Treasure Chest

**Query:** "What color was the key?"  
**Expected:** "Blue"

## Installation

```bash
pip install sentence-transformers numpy torch

# Verify Ollama
curl http://localhost:11434/api/generate -d '{"model":"llama3.2:1b","prompt":"Hi","stream":false}'
```

## Running

```bash
python3 src/run_experiment.py
# Runtime: 10-15 minutes
# Output: logs/ and results/
```

## Configuration

Edit `config/experiment.yaml`:

```yaml
experiment:
  num_trials: 5

model:
  name: "llama3.2:1b"
  url: "http://localhost:11434"

strategies:
  select:
    top_k: 3
  compress:
    compression_interval: 3
  write:
    scratchpad_keys: ["inventory", "npcs", "knowledge", "locations"]
```

## Expected Results

| Strategy | Accuracy | Latency | LLM Calls |
|----------|----------|---------|-----------|
| SELECT | 80-90% | 2-3s | 1 |
| COMPRESS | 40-60% | 5-8s | 4-5 |
| WRITE | 85-95% | 8-12s | 11 |

**Key Insights:**
- SELECT: Best efficiency (1 LLM call)
- COMPRESS: Loses specific details in summarization
- WRITE: Best accuracy via structured extraction
