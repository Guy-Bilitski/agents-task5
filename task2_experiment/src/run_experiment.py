"""Task 2: Context Window Size Experiment."""

import sys
import time
from pathlib import Path
from typing import Dict, Any, List

# Add root to path to allow importing common
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common import setup_logger, set_seed, load_yaml_config, save_json_results, MockLLM, generate_text_block, insert_needle

def run_experiment():
    # Load Config
    config_path = Path(__file__).parent.parent / "config" / "experiment.yaml"
    config = load_yaml_config(config_path)
    
    # Setup
    logger = setup_logger(
        name=config['experiment']['name'],
        log_dir=Path(config['logging']['log_dir']),
        level=config['logging']['level'],
        console=config['logging']['console'],
        file=config['logging']['file']
    )
    
    set_seed(config['experiment']['seed'])
    
    logger.info("Starting Experiment 2: Context Window Size Impact")
    logger.info(f"Testing Doc Counts: {config['dataset']['doc_counts']}")
    
    # Initialize Model
    model = MockLLM(
        latency_base=config['model']['latency_base'],
        latency_per_token=config['model']['latency_per_token'],
        noise_threshold=config['model']['noise_threshold'],
        noise_prob_low=config['model']['noise_prob_low'],
        noise_prob_high=config['model']['noise_prob_high']
    )
    
    results = []
    
    # Iterate through scaling levels
    for count in config['dataset']['doc_counts']:
        logger.info(f"\n--- Testing with {count} Documents ---")
        
        # 1. Generate Data
        full_text = ""
        for _ in range(count):
            full_text += generate_text_block(domain="generic", min_words=config['dataset']['words_per_doc']) + "\n\n"
            
        # Insert Needle randomly
        full_text = insert_needle(full_text, config['dataset']['needle'], position="random")
        
        # 2. Query Model
        logger.info(f"Context Length: ~{len(full_text.split())} words")
        result = model.query(
            context=full_text,
            question=config['dataset']['query'],
            expected_answer=config['dataset']['needle']
        )
        
        logger.info(f"Result: Latency={result['latency']:.4f}s | Accurate={result['is_accurate']}")
        
        # 3. Store
        results.append({
            "doc_count": count,
            "estimated_tokens": result['token_count'],
            "latency": result['latency'],
            "accuracy": 1 if result['is_accurate'] else 0
        })
        
    # Final Report
    logger.info("\n=== FINAL REPORT ===")
    logger.info(f"{'Docs':<6} | {'Tokens':<10} | {'Latency':<10} | {'Accuracy':<10}")
    for r in results:
        logger.info(f"{r['doc_count']:<6} | {r['estimated_tokens']:<10} | {r['latency']:<10.4f} | {r['accuracy']:<10}")
        
    save_json_results(results, Path(config['output']['results_dir']))
    logger.info(f"Results saved to {config['output']['results_dir']}")

if __name__ == "__main__":
    run_experiment()
