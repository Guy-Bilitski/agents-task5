"""Mock LLM Simulator."""

import time
import random
from typing import Dict, Any

from common.llm import BaseLLM # Import BaseLLM

class MockLLM(BaseLLM): # Inherit from BaseLLM
    """Simulates LLM behavior for Latency and Accuracy experiments."""
    
    def __init__(
        self, 
        full_context_latency_base: float,
        full_context_latency_per_word: float,
        full_context_noise_prob: float,
        rag_latency_retrieval: float,
        rag_latency_generation: float,
        rag_noise_prob: float
    ):
        """
        Initialize simulator.
        config should come from SimulationConfig
        """
        self.latency_base = full_context_latency_base
        self.latency_per_word = full_context_latency_per_word
        self.full_noise_prob = full_context_noise_prob
        
        self.rag_latency = rag_latency_retrieval + rag_latency_generation
        self.rag_noise_prob = rag_noise_prob

    def query(self, context: str, question: str, needle_fact: str) -> Dict[str, Any]:
        """
        Simulate an LLM query.
        
        Args:
            context: The prompt context
            question: The user query
            needle_fact: The secret fact we are looking for (to verify if it's in context)
            
        Returns:
            Dict with 'response', 'latency', 'is_accurate'
        """
        start_time = time.time()
        
        # Analyze Context
        context_words = len(context.split())
        has_needle = needle_fact in context
        
        # Determine Mode based on context length (Heuristic)
        # RAG usually < 2000 words (3 chunks * 500), Full Context ~10000 words
        is_full_context = context_words > 3000
        
        # Simulate Latency
        if is_full_context:
            # Simulate linear complexity for attention mechanism
            process_time = self.latency_base + (context_words * self.latency_per_word)
            # Add some randomness
            process_time *= random.uniform(0.9, 1.1)
            time.sleep(min(process_time, 2.0)) # Cap at 2s for runtime sanity during dev, but record full time
            
            # Simulate "Lost in the Middle"
            # If needle is present, chance to miss it due to noise
            if has_needle:
                success = random.random() > self.full_noise_prob
            else:
                success = False # Cannot answer if not there
                
        else:
            # RAG Mode
            time.sleep(self.rag_latency)
            process_time = self.rag_latency
            
            if has_needle:
                success = random.random() > self.rag_noise_prob
            else:
                success = False # Correctly identifies it doesn't know? Or fails? 
                # Task says RAG should be accurate. If retrieval failed (no needle), 
                # accurate response is "I don't know". But for this binary pass/fail, 
                # we assume retrieval SHOULD have found it.
                
        # Generate Response
        if success and has_needle:
            response = f"Based on the context, the answer is: {needle_fact}"
            is_accurate = True
        elif not has_needle:
             response = "I cannot answer this question from the provided context."
             is_accurate = False # Technically accurate behavior, but for the experiment finding the needle, it's a fail to retrieve
        else:
            # Hallucination / Missed
            response = "The documents discuss various topics including law and technology, but I cannot find specific details about Drug X side effects."
            is_accurate = False
            
        total_latency = time.time() - start_time
        # Use calculated process_time for consistency if sleep was capped, 
        # or just use real elapsed time. Let's use real elapsed.
        
        return {
            "response": response,
            "latency": total_latency,
            "is_accurate": is_accurate,
            "context_length": context_words
        }
