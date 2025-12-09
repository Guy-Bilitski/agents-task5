"""Lost in the Middle Experiment - Minimal Version"""

import yaml
import requests
from utils import setup_logging, set_seed, generate_document, save_results


def load_config(path="config.yaml"):
    """Load configuration from YAML."""
    with open(path) as f:
        return yaml.safe_load(f)


def query_llm(text, question, config):
    """Query LLM via Ollama API."""
    prompt = f"""You are a helpful assistant. Answer the question using ONLY the provided Context. If the answer is in the context, output it directly.

Context:
{text}

Question: {question}

Answer:"""
    
    response = requests.post(
        config['model_url'],
        json={
            "model": config['model_name'],
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": config['temperature'],
                "num_predict": config['max_tokens']
            }
        },
        timeout=60
    )
    
    return response.json().get('response', '').strip()


def evaluate(response, expected):
    """Check if expected answer is in response."""
    return 1 if expected.lower() in response.lower() else 0


def run_experiment():
    """Run the experiment."""
    # Setup
    config = load_config()
    logger = setup_logging()
    set_seed(config['seed'])
    
    logger.info("=" * 60)
    logger.info("Lost in the Middle Experiment")
    logger.info("=" * 60)
    
    # Prepare test cases
    test_cases = [
        ('start', config['positions']['start']),
        ('middle', config['positions']['middle']),
        ('middle', config['positions']['middle']),
        ('middle', config['positions']['middle']),
        ('end', config['positions']['end']),
    ]
    
    results = {'documents': [], 'scores': {'start': [], 'middle': [], 'end': []}}
    
    # Run tests
    for i, (position, pct) in enumerate(test_cases, 1):
        logger.info(f"\n[{i}/{len(test_cases)}] Testing {position.upper()} position ({pct*100:.0f}%)")
        
        # Generate document
        doc = generate_document(pct, config['doc_length'], config['critical_fact'])
        logger.info(f"  Generated: {doc['word_count']} words")
        
        # Query LLM
        response = query_llm(doc['text'], config['query'], config)
        logger.info(f"  Response: '{response}'")
        
        # Evaluate
        score = evaluate(response, config['expected_answer'])
        results['scores'][position].append(score)
        
        result_str = "✓ PASS" if score else "✗ FAIL"
        logger.info(f"  Result: {result_str}")
        
        results['documents'].append({
            'id': i,
            'position': position,
            'position_pct': doc['position_pct'],
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
            stats[pos] = {'accuracy': acc, 'count': len(scores)}
            logger.info(f"{pos.upper()}: {acc*100:.0f}% ({sum(scores)}/{len(scores)})")
    
    # Conclusion
    edge_acc = (stats['start']['accuracy'] + stats['end']['accuracy']) / 2
    middle_acc = stats['middle']['accuracy']
    
    logger.info(f"\nEdge (start+end): {edge_acc*100:.0f}%")
    logger.info(f"Middle: {middle_acc*100:.0f}%")
    
    if edge_acc > middle_acc:
        logger.info("\n✓ Hypothesis CONFIRMED: Better retrieval at edges")
    else:
        logger.info("\n✗ Hypothesis NOT confirmed")
    
    # Save results
    results['statistics'] = stats
    results['config'] = config
    output_file = save_results(results)
    logger.info(f"\n📊 Saved to: {output_file}")


if __name__ == "__main__":
    run_experiment()
