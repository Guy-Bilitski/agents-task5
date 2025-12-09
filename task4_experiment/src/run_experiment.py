"""Task 4: Run Experiment."""

import sys
from pathlib import Path

# Add root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common import setup_logger, set_seed, load_yaml_config, save_json_results
from task4_experiment.src.strategies import ContextStrategies

def generate_action_sequence() -> list:
    return [
        "Found a Blue Key under the mat.",
        "Unlocked the heavy Oak Door.",
        "Entered the hallway and saw a Red Painting.",
        "Spoke to the Guard named Steve.",
        "Steve asked for a password.",
        "Found a note saying the password is 'Shadow'.",
        "Gave password to Steve.",
        "Steve opened the Gate.",
        "Entered the Garden.",
        "Found the Treasure Chest."
    ]

def run_experiment():
    config_path = Path(__file__).parent.parent / "config" / "experiment.yaml"
    config = load_yaml_config(config_path)
    
    logger = setup_logger(
        name=config['experiment']['name'],
        log_dir=Path(config['logging']['log_dir']),
        level=config['logging']['level']
    )
    
    set_seed(config['experiment']['seed'])
    logger.info("Starting Experiment 4: Context Strategies")
    
    history = generate_action_sequence()
    logger.info(f"Generated {len(history)} step action sequence.")
    
    query = config['simulation']['query']
    target = config['simulation']['target_answer']
    logger.info(f"Query: '{query}' | Target: '{target}'")
    
    results = {}
    
    # --- 1. SELECT Strategy ---
    logger.info("\n--- Strategy A: SELECT ---")
    ctx_select = ContextStrategies.select_strategy(
        history, 
        query, 
        top_k=config['strategies']['select']['top_k']
    )
    logger.info(f"Context:\n{ctx_select}")
    pass_select = target.lower() in ctx_select.lower()
    logger.info(f"Result: {'PASS' if pass_select else 'FAIL'}")
    results['select'] = {'pass': pass_select, 'context': ctx_select}

    # --- 2. COMPRESS Strategy ---
    logger.info("\n--- Strategy B: COMPRESS ---")
    ctx_compress = ContextStrategies.compress_strategy(
        history,
        max_tokens=config['simulation']['max_tokens_limit']
    )
    logger.info(f"Context:\n{ctx_compress}")
    # Compression mock summary doesn't include "Blue", just "found items"
    pass_compress = target.lower() in ctx_compress.lower()
    logger.info(f"Result: {'PASS' if pass_compress else 'FAIL'}")
    results['compress'] = {'pass': pass_compress, 'context': ctx_compress}

    # --- 3. WRITE Strategy ---
    logger.info("\n--- Strategy C: WRITE ---")
    scratchpad = {'inventory': [], 'npcs': [], 'knowledge': []}
    for step in history:
        scratchpad = ContextStrategies.write_strategy(step, scratchpad)
    
    ctx_write = str(scratchpad)
    logger.info(f"Context:\n{ctx_write}")
    pass_write = target.lower() in ctx_write.lower()
    logger.info(f"Result: {'PASS' if pass_write else 'FAIL'}")
    results['write'] = {'pass': pass_write, 'context': ctx_write}
    
    # Final Report
    logger.info("\n=== FINAL SUMMARY ===")
    logger.info(f"SELECT:   {'PASS' if pass_select else 'FAIL'}")
    logger.info(f"COMPRESS: {'PASS' if pass_compress else 'FAIL'}")
    logger.info(f"WRITE:    {'PASS' if pass_write else 'FAIL'}")
    
    save_json_results(results, Path(config['output']['results_dir']))

if __name__ == "__main__":
    run_experiment()
