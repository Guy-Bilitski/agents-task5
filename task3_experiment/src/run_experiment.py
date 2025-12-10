"""Main experiment runner for Task 3: RAG vs Full Context."""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, TYPE_CHECKING

# Add root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common import setup_logger, set_seed, save_json_results
from task3_experiment.src.config import load_config, Config
from task3_experiment.src.data.generator import generate_dataset
from task3_experiment.src.rag.indexer import VectorStore
from task3_experiment.src.models.simulator import MockLLM
from task3_experiment.src.evaluation.metrics import calculate_statistics

def run_mode_a_full_context(config: Config, documents: List[Any], llm: MockLLM, logger) -> Dict[str, Any]:
    """Execute Mode A: Full Context."""
    logger.info("--- [Mode A] Starting Full Context Execution ---")
    
    # Concatenate ALL documents
    full_context = "\n\n".join([d.text for d in documents])
    logger.info(f"Full Context Size: {len(full_context.split())} words")
    
    # Query LLM
    result = llm.query(
        context=full_context, 
        question=config.dataset.needle.query,
        needle_fact=config.dataset.needle.fact
    )
    
    logger.info(f"Mode A Result: Latency={result['latency']:.4f}s | Accurate={result['is_accurate']}")
    return result

def run_mode_b_rag(config: Config, documents: List[Any], llm: MockLLM, logger) -> Dict[str, Any]:
    """Execute Mode B: RAG."""
    logger.info("--- [Mode B] Starting RAG Execution ---")
    
    # 1. Indexing
    logger.info("Indexing documents...")
    start_index = time.perf_counter()
    vector_store = VectorStore(
        chunk_size=config.rag.chunk_size,
        overlap=config.rag.chunk_overlap
    )
    vector_store.add_documents(documents)
    index_time = time.perf_counter() - start_index
    logger.info(f"Indexing complete in {index_time:.4f}s. Total chunks: {vector_store.total_chunks}")
    
    # 2. Retrieval
    logger.info(f"Retrieving Top-{config.rag.top_k} chunks...")
    retrieval_start = time.perf_counter()
    relevant_chunks = vector_store.similarity_search(
        query=config.dataset.needle.query,
        k=config.rag.top_k
    )
    retrieval_time = time.perf_counter() - retrieval_start
    
    # Log retrieved chunks
    for i, chunk in enumerate(relevant_chunks):
        logger.debug(f"Chunk {i+1} (Doc {chunk.doc_id}): {chunk.text[:50]}...")
        if chunk.metadata['has_needle']:
            logger.info(f"✓ Retrieved chunk containing needle (Doc {chunk.doc_id})")

    # 3. Context Construction
    rag_context = "\n\n".join([c.text for c in relevant_chunks])
    
    # 4. Generation
    # We pass the RAG context to the LLM
    # Note: We add retrieval_time to the total latency in the result manually 
    # or consider it part of the system latency. 
    # The MockLLM simulates generation latency. We should add retrieval time.
    
    result = llm.query(
        context=rag_context,
        question=config.dataset.needle.query,
        needle_fact=config.dataset.needle.fact
    )
    
    # Add retrieval overhead to latency
    total_rag_latency = retrieval_time + result['latency']
    result['latency'] = total_rag_latency
    result['retrieval_time'] = retrieval_time
    
    logger.info(f"Mode B Result: Latency={result['latency']:.4f}s | Accurate={result['is_accurate']}")
    return result

def main():
    # Load Config
    config = load_config()
    
    # Setup Logger
    logger = setup_logger(
        name=config.experiment.name,
        log_dir=Path(config.logging.log_dir),
        level=config.logging.level,
        console=config.logging.console,
        file=config.logging.file
    )
    
    logger.info(f"Initialized Experiment: {config.experiment.name}")
    
    # Initialize Simulator
    # Need to pass individual simulation params
    sim_config = config.simulation
    llm = MockLLM(
        full_context_latency_base=sim_config.full_context_latency_base,
        full_context_latency_per_word=sim_config.full_context_latency_per_word,
        full_context_noise_prob=sim_config.full_context_noise_prob,
        rag_latency_retrieval=sim_config.rag_latency_retrieval,
        rag_latency_generation=sim_config.rag_latency_generation,
        rag_noise_prob=sim_config.rag_noise_prob
    )
    
    # Storage for results
    results_a = []
    results_b = []
    
    # Run N iterations to get stable stats
    iterations = 5
    logger.info(f"Running {iterations} iterations...")
    
    for i in range(iterations):
        logger.info(f"\n=== Iteration {i+1}/{iterations} ===")
        
        # Generate Fresh Data
        documents = generate_dataset(config.dataset)
        
        # Run Mode A
        res_a = run_mode_a_full_context(config, documents, llm, logger)
        results_a.append(res_a)
        
        # Run Mode B
        res_b = run_mode_b_rag(config, documents, llm, logger)
        results_b.append(res_b)
        
    # Analyze
    stats_a = calculate_statistics(results_a)
    stats_b = calculate_statistics(results_b)
    
    # Report
    logger.info("\n" + "="*50)
    logger.info("FINAL COMPARATIVE REPORT")
    logger.info("="*50)
    
    logger.info(f"MODE A (Full Context):")
    logger.info(f"  Avg Latency: {stats_a['avg_latency']:.4f}s")
    logger.info(f"  Accuracy:    {stats_a['accuracy']:.1f}%")
    
    logger.info(f"\nMODE B (RAG):")
    logger.info(f"  Avg Latency: {stats_b['avg_latency']:.4f}s")
    logger.info(f"  Accuracy:    {stats_b['accuracy']:.1f}%")
    
    # Comparison
    latency_reduction = ((stats_a['avg_latency'] - stats_b['avg_latency']) / stats_a['avg_latency']) * 100
    logger.info(f"\nLatency Reduction: {latency_reduction:.1f}%")
    
    if stats_b['accuracy'] > stats_a['accuracy']:
        logger.info("Conclusion: RAG strategy successfully filtered noise and improved efficiency.")
    elif stats_b['accuracy'] == stats_a['accuracy'] and latency_reduction > 0:
         logger.info("Conclusion: RAG strategy matched accuracy but significantly improved efficiency.")
    else:
        logger.info("Conclusion: Results inconclusive or unexpected.")

    # Save Results
    save_json_results(
        results={
            "config": config.experiment.__dict__,
            "stats_a": stats_a,
            "stats_b": stats_b,
            "raw_results_a": results_a,
            "raw_results_b": results_b
        }, 
        output_dir=Path(config.output.results_dir)
    )
    logger.info(f"Report saved to {config.output.results_dir}")

if __name__ == "__main__":
    main()
