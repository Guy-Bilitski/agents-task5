# Task 1: Lost in the Middle

## Overview
This experiment tests whether LLMs retrieve facts better from the start/end of documents versus the middle, a phenomenon known as "Lost in the Middle."

## Hypothesis
Facts placed at the edges (start/end) of context are retrieved more accurately than facts in the middle.

## Methodology
- Generate documents of fixed length with a critical fact inserted at different positions
- Test positions: Start (0%), Middle (50%), End (100%)
- Query the LLM to retrieve the critical fact
- Compare accuracy across positions to test the hypothesis

## Running
```bash
python3 src/run_experiment.py
```

## Configuration
Edit `config/experiment.yaml` to customize:
- `doc_length`: Number of words per document
- `critical_fact`: The needle to hide in the haystack
- `positions`: Test positions (start, middle, end percentages)
- `model`: Ollama model configuration

## Expected Results
- **Start/End positions**: Higher accuracy (edges are remembered better)
- **Middle position**: Lower accuracy (information gets "lost")

## Output
- Logs: `logs/lost_in_the_middle.log`
- Results: `results/results_<timestamp>.json`
