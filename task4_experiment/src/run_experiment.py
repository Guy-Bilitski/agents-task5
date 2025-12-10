"""Task 4: Real Multi-Step Agent Experiment with Memory Strategies."""

import sys
import time
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

# Add root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common import setup_logger, set_seed, load_yaml_config, save_json_results, OllamaLLM
from task4_experiment.src.agent import Agent
from task4_experiment.src.memory_strategies import SelectStrategy, CompressStrategy, WriteStrategy


def generate_action_sequence() -> List[str]:
    """Generate a sequence of actions for the agent to process."""
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


def evaluate_answer(response: str, expected: str, logger) -> bool:
    """Evaluate if the answer contains the expected information."""
    # Check if expected answer appears in response (case-insensitive)
    result = expected.lower() in response.lower()
    
    if logger:
        if result:
            logger.info(f"✓ Correct answer detected: '{expected}' found in response")
        else:
            logger.warning(f"✗ Incorrect: '{expected}' NOT found in response: '{response}'")
    
    return result


def run_single_trial(strategy_name: str, strategy_instance, llm, config: Dict, logger) -> Dict[str, Any]:
    """Run a single trial with a specific strategy."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Running {strategy_name} Strategy")
    logger.info(f"{'='*60}")
    
    trial_start = time.time()
    
    # Create agent with strategy
    agent = Agent(llm=llm, memory_strategy=strategy_instance, logger=logger)
    
    # Generate and process action sequence
    actions = generate_action_sequence()
    logger.info(f"Processing {len(actions)} sequential actions...")
    
    agent.process_action_sequence(actions)
    
    # Query the agent
    question = config['scenario']['query']
    expected = config['scenario']['expected_answer']
    
    logger.info(f"\nQuerying agent: '{question}'")
    logger.info(f"Expected answer: '{expected}'")
    
    result = agent.answer_question(question)
    
    # Evaluate
    is_correct = evaluate_answer(result['response'], expected, logger)
    
    # Calculate total time
    total_time = time.time() - trial_start
    
    # Get comprehensive metrics
    metrics = agent.get_full_metrics()
    
    # Compile results
    trial_result = {
        'strategy': strategy_name,
        'correct': is_correct,
        'response': result['response'],
        'llm_response_latency': result['latency'],
        'total_trial_time': total_time,
        'llm_calls': metrics['llm_calls'],
        'total_tokens': metrics.get('total_tokens', 0),
        'context_used': result.get('context_used', ''),
        'additional_metrics': metrics
    }
    
    # Log summary
    logger.info(f"\n{'-'*60}")
    logger.info(f"Trial Summary for {strategy_name}:")
    logger.info(f"  Accuracy: {'CORRECT' if is_correct else 'INCORRECT'}")
    logger.info(f"  Total Time: {total_time:.2f}s")
    logger.info(f"  LLM Calls: {metrics['llm_calls']}")
    logger.info(f"  Total Tokens: {metrics.get('total_tokens', 'N/A')}")
    logger.info(f"{'-'*60}")
    
    return trial_result


def run_experiment():
    """Main experiment runner."""
    config_path = Path(__file__).parent.parent / "config" / "experiment.yaml"
    config = load_yaml_config(config_path)
    
    # Setup logger
    logger = setup_logger(
        name=config['experiment']['name'],
        log_dir=Path(config['logging']['log_dir']),
        level=config['logging']['level'],
        console=config['logging']['console'],
        file=config['logging']['file']
    )
    
    logger.info("="*70)
    logger.info(f"Starting Experiment 4: {config['experiment']['name']}")
    logger.info(f"Version: {config['experiment']['version']}")
    logger.info(f"Number of trials per strategy: {config['experiment']['num_trials']}")
    logger.info("="*70)
    
    set_seed(config['experiment']['seed'])
    
    # Initialize LLM
    logger.info(f"\nInitializing LLM: {config['model']['name']} at {config['model']['url']}")
    llm = OllamaLLM(
        model_name=config['model']['name'],
        base_url=config['model']['url'],
        temperature=config['model']['temperature'],
        max_tokens=config['model']['max_tokens'],
        timeout=config['model']['timeout']
    )
    
    # Storage for all results
    all_results = {
        'config': config,
        'trials': {
            'SELECT': [],
            'COMPRESS': [],
            'WRITE': []
        },
        'statistics': {}
    }
    
    num_trials = config['experiment']['num_trials']
    
    # Run trials for each strategy
    for trial_num in range(1, num_trials + 1):
        logger.info(f"\n\n{'#'*70}")
        logger.info(f"# TRIAL {trial_num}/{num_trials}")
        logger.info(f"{'#'*70}\n")
        
        # SELECT Strategy
        select_strategy = SelectStrategy(
            top_k=config['strategies']['select']['top_k'],
            embedding_model=config['strategies']['select']['embedding_model']
        )
        select_result = run_single_trial('SELECT', select_strategy, llm, config, logger)
        all_results['trials']['SELECT'].append(select_result)
        
        # COMPRESS Strategy
        compress_strategy = CompressStrategy(
            compression_interval=config['strategies']['compress']['compression_interval'],
            max_recent=config['strategies']['compress']['max_recent']
        )
        compress_result = run_single_trial('COMPRESS', compress_strategy, llm, config, logger)
        all_results['trials']['COMPRESS'].append(compress_result)
        
        # WRITE Strategy
        write_strategy = WriteStrategy()
        write_result = run_single_trial('WRITE', write_strategy, llm, config, logger)
        all_results['trials']['WRITE'].append(write_result)
    
    # Calculate statistics
    logger.info(f"\n\n{'='*70}")
    logger.info("COMPUTING STATISTICS ACROSS ALL TRIALS")
    logger.info(f"{'='*70}\n")
    
    for strategy_name in ['SELECT', 'COMPRESS', 'WRITE']:
        trials = all_results['trials'][strategy_name]
        
        # Extract metrics
        accuracies = [1 if t['correct'] else 0 for t in trials]
        latencies = [t['total_trial_time'] for t in trials]
        llm_calls = [t['llm_calls'] for t in trials]
        tokens = [t['total_tokens'] for t in trials]
        
        # Calculate statistics
        stats = {
            'accuracy': {
                'mean': np.mean(accuracies),
                'std': np.std(accuracies),
                'successes': sum(accuracies),
                'total': len(accuracies)
            },
            'latency': {
                'mean': np.mean(latencies),
                'std': np.std(latencies),
                'min': np.min(latencies),
                'max': np.max(latencies)
            },
            'llm_calls': {
                'mean': np.mean(llm_calls),
                'std': np.std(llm_calls),
                'total': sum(llm_calls)
            },
            'tokens': {
                'mean': np.mean(tokens),
                'std': np.std(tokens),
                'total': sum(tokens)
            }
        }
        
        all_results['statistics'][strategy_name] = stats
        
        # Log statistics
        logger.info(f"\n{strategy_name} Strategy Statistics:")
        logger.info(f"  Accuracy: {stats['accuracy']['mean']*100:.1f}% ± {stats['accuracy']['std']*100:.1f}% ({stats['accuracy']['successes']}/{stats['accuracy']['total']})")
        logger.info(f"  Latency: {stats['latency']['mean']:.2f}s ± {stats['latency']['std']:.2f}s")
        logger.info(f"  LLM Calls: {stats['llm_calls']['mean']:.1f} ± {stats['llm_calls']['std']:.1f} (total: {stats['llm_calls']['total']})")
        logger.info(f"  Tokens: {stats['tokens']['mean']:.0f} ± {stats['tokens']['std']:.0f} (total: {stats['tokens']['total']})")
    
    # Final comparative analysis
    logger.info(f"\n{'='*70}")
    logger.info("FINAL COMPARATIVE ANALYSIS")
    logger.info(f"{'='*70}\n")
    
    logger.info(f"{'Strategy':<12} | {'Accuracy':<15} | {'Latency':<15} | {'Calls':<10} | {'Tokens':<10}")
    logger.info(f"{'-'*12}-+-{'-'*15}-+-{'-'*15}-+-{'-'*10}-+-{'-'*10}")
    
    for strategy_name in ['SELECT', 'COMPRESS', 'WRITE']:
        stats = all_results['statistics'][strategy_name]
        logger.info(
            f"{strategy_name:<12} | "
            f"{stats['accuracy']['mean']*100:>5.1f}% ± {stats['accuracy']['std']*100:>4.1f}% | "
            f"{stats['latency']['mean']:>6.2f}s ± {stats['latency']['std']:>4.2f}s | "
            f"{stats['llm_calls']['mean']:>5.1f} ± {stats['llm_calls']['std']:>2.1f} | "
            f"{stats['tokens']['mean']:>5.0f} ± {stats['tokens']['std']:>3.0f}"
        )
    
    # Efficiency metrics
    logger.info(f"\n{'='*70}")
    logger.info("EFFICIENCY ANALYSIS")
    logger.info(f"{'='*70}\n")
    
    for strategy_name in ['SELECT', 'COMPRESS', 'WRITE']:
        stats = all_results['statistics'][strategy_name]
        acc = stats['accuracy']['mean']
        lat = stats['latency']['mean']
        tok = stats['tokens']['mean']
        
        # Calculate efficiency scores
        accuracy_per_second = acc / lat if lat > 0 else 0
        accuracy_per_token = acc / tok if tok > 0 else 0
        
        logger.info(f"{strategy_name}:")
        logger.info(f"  Accuracy per Second: {accuracy_per_second:.4f}")
        logger.info(f"  Accuracy per Token: {accuracy_per_token:.6f}")
    
    # Save results
    try:
        output_file = save_json_results(all_results, Path(config['output']['results_dir']))
        logger.info(f"\n{'='*70}")
        logger.info(f"Results saved to: {output_file}")
        logger.info(f"{'='*70}")
    except Exception as e:
        logger.error(f"Failed to save results: {e}")
    
    logger.info("\nExperiment completed successfully!")


if __name__ == "__main__":
    run_experiment()
