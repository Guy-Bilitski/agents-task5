"""Task 1: Lost in the Middle Experiment."""

import sys
import requests
from pathlib import Path

# Add root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common import setup_logger, set_seed, load_yaml_config, save_json_results, generate_text_block, insert_needle


def query_llm(text: str, question: str, config: dict) -> str:
    """Query LLM via Ollama API."""
    prompt = f"""You are a helpful assistant. Answer the question using ONLY the provided Context. If the answer is in the context, output it directly.

Context:
{text}

Question: {question}

Answer:"""

    try:
        response = requests.post(
            config['model']['url'],
            json={
                "model": config['model']['name'],
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": config['model']['temperature'],
                    "num_predict": config['model']['max_tokens']
                }
            },
            timeout=60
        )
        return response.json().get('response', '').strip()
    except Exception as e:
        return f"ERROR: {str(e)}"


def evaluate(response: str, expected: str) -> int:
    """Check if expected answer is in response."""
    return 1 if expected.lower() in response.lower() else 0


def run_experiment():
    """Run the Lost in the Middle experiment."""
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "experiment.yaml"
    config = load_yaml_config(config_path)

    # Setup logging
    logger = setup_logger(
        name=config['experiment']['name'],
        log_dir=Path(config['logging']['log_dir']),
        level=config['logging']['level'],
        console=config['logging']['console'],
        file=config['logging']['file']
    )

    set_seed(config['experiment']['seed'])

    logger.info("=" * 60)
    logger.info(f"Experiment: {config['experiment']['name']}")
    logger.info("=" * 60)
    logger.info(f"Hypothesis: Facts at edges (start/end) are retrieved better than middle")

    # Prepare results storage
    results = {
        'documents': [],
        'scores': {'start': [], 'middle': [], 'end': []}
    }

    # Run test cases
    test_cases = config['dataset']['test_cases']

    for i, (position, pct) in enumerate(test_cases, 1):
        logger.info(f"\n[{i}/{len(test_cases)}] Testing {position.upper()} position ({pct*100:.0f}%)")

        # Generate document with needle at specified position
        filler_text = generate_text_block(
            domain="generic",
            min_words=config['dataset']['doc_length']
        )

        # Insert the critical fact at the specified position
        document_text = insert_needle(
            text=filler_text,
            needle=config['dataset']['critical_fact'],
            position=pct
        )

        word_count = len(document_text.split())
        logger.info(f"  Generated: {word_count} words")

        # Query LLM
        response = query_llm(
            text=document_text,
            question=config['dataset']['query'],
            config=config
        )
        logger.info(f"  Response: '{response}'")

        # Evaluate
        score = evaluate(response, config['dataset']['expected_answer'])
        results['scores'][position].append(score)

        result_str = "✓ PASS" if score else "✗ FAIL"
        logger.info(f"  Result: {result_str}")

        results['documents'].append({
            'id': i,
            'position': position,
            'position_pct': pct * 100,
            'word_count': word_count,
            'response': response,
            'score': score
        })

    # Calculate statistics
    logger.info("\n" + "=" * 60)
    logger.info("RESULTS")
    logger.info("=" * 60)

    stats = {}
    for pos in ['start', 'middle', 'end']:
        scores = results['scores'][pos]
        if scores:
            acc = sum(scores) / len(scores)
            stats[pos] = {
                'accuracy': acc,
                'count': len(scores),
                'correct': sum(scores)
            }
            logger.info(f"{pos.upper():>6}: {acc*100:>5.0f}% ({sum(scores)}/{len(scores)})")

    # Test hypothesis
    edge_acc = (stats['start']['accuracy'] + stats['end']['accuracy']) / 2
    middle_acc = stats['middle']['accuracy']

    logger.info(f"\nEdge (start+end): {edge_acc*100:.0f}%")
    logger.info(f"Middle:           {middle_acc*100:.0f}%")

    if edge_acc > middle_acc:
        logger.info("\n✓ Hypothesis CONFIRMED: Better retrieval at edges")
    else:
        logger.info("\n✗ Hypothesis NOT confirmed")

    # Save results
    results['statistics'] = stats
    results['config'] = config

    output_file = save_json_results(results, Path(config['output']['results_dir']))
    logger.info(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    run_experiment()
