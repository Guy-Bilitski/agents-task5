# Task 1: Lost in the Middle

Tests if LLMs retrieve facts better from start/end vs middle of context.

## Run
```bash
python3 experiment.py
```

## Configure
Edit `config.yaml`: doc count, length, model, fact to test.

## Output
- `results/results_*.json` - Stats & accuracy by position
- `experiment.log` - Run log
