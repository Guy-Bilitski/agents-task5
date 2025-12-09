"""Common LLM interfaces and Mock implementations."""

import time
import random
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseLLM(ABC):
    """Abstract base class for LLMs."""
    
    @abstractmethod
    def query(self, context: str, question: str, **kwargs) -> Dict[str, Any]:
        """
        Query the LLM.
        
        Args:
            context: Input context
            question: User query
            **kwargs: Additional args (e.g., ground truth for mocks)
            
        Returns:
            Dict containing 'response', 'latency', 'is_accurate' (if verifiable)
        """
        pass

class MockLLM(BaseLLM):
    """
    Configurable Mock LLM.
    Can simulate:
    1. Latency based on context length.
    2. Accuracy degradation based on noise/length ("Lost in the Middle").
    """
    
    def __init__(
        self,
        latency_base: float = 0.5,
        latency_per_token: float = 0.0005,
        noise_threshold: int = 5000,
        noise_prob_low: float = 0.0,
        noise_prob_high: float = 0.5
    ):
        self.latency_base = latency_base
        self.latency_per_token = latency_per_token
        self.noise_threshold = noise_threshold
        self.noise_prob_low = noise_prob_low
        self.noise_prob_high = noise_prob_high

    def query(self, context: str, question: str, **kwargs) -> Dict[str, Any]:
        start_time = time.time()
        
        # Estimate tokens (approx 1.3 chars per token or just split words)
        # Using simple word count for consistency across experiments
        token_count = len(context.split())
        
        # Simulate Latency
        process_time = self.latency_base + (token_count * self.latency_per_token)
        # Add jitter
        process_time *= random.uniform(0.9, 1.1)
        
        # Determine Accuracy
        # "Lost in the Middle" / Saturation effect
        if token_count > self.noise_threshold:
            failure_prob = self.noise_prob_high
        else:
            failure_prob = self.noise_prob_low
            
        is_accurate = random.random() > failure_prob
        
        # Check expected answer if provided
        needle = kwargs.get('expected_answer', '')
        if needle and is_accurate:
            response = f"The answer is {needle}."
        elif not is_accurate:
            response = "I am unsure based on the context."
        else:
            # Fallback for generic queries
            response = "Simulated Response"

        # Sleep (Simulate API call)
        # Cap sleep for dev speed, but report full calculated latency?
        # Let's sleep a fraction of it to keep tests fast, unless 'real_time' flag is passed.
        # For this environment, we'll just sleep the full amount up to a limit.
        time.sleep(min(process_time, 1.0)) 
        
        # Record actual elapsed or simulated? 
        # Usually for experiments we want the simulated latency metric if we are mocking hardware.
        # But let's return the calculated process_time as 'latency' to match the physics we defined.
        
        return {
            "response": response,
            "latency": process_time,
            "token_count": token_count,
            "is_accurate": is_accurate
        }
