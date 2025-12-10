"""Multi-step Agent with different memory management strategies."""

import time
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

class MemoryStrategy(ABC):
    """Abstract base class for memory management strategies."""
    
    @abstractmethod
    def process_step(self, step: str, llm, **kwargs) -> None:
        """Process a single step and update memory."""
        pass
    
    @abstractmethod
    def query(self, question: str, llm, **kwargs) -> Dict[str, Any]:
        """Query the memory to answer a question."""
        pass
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Return metrics about memory usage."""
        pass


class Agent:
    """Multi-step agent with configurable memory strategy."""
    
    def __init__(self, llm, memory_strategy: MemoryStrategy, logger=None):
        self.llm = llm
        self.memory = memory_strategy
        self.logger = logger
        self.history = []
        self.step_count = 0
        
    def process_action_sequence(self, actions: List[str]) -> None:
        """Process a sequence of actions step by step."""
        if self.logger:
            self.logger.info(f"Agent processing {len(actions)} actions with {self.memory.__class__.__name__}")
        
        for i, action in enumerate(actions):
            if self.logger:
                self.logger.debug(f"Step {i+1}/{len(actions)}: {action}")
            
            self.history.append(action)
            self.step_count += 1
            
            # Let the memory strategy process this step
            self.memory.process_step(action, self.llm, step_number=i+1, logger=self.logger)
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a question using the memory strategy."""
        if self.logger:
            self.logger.info(f"Agent answering: '{question}'")
        
        result = self.memory.query(question, self.llm, logger=self.logger)
        
        # Add agent-level metrics
        result['total_steps'] = self.step_count
        result['history_length'] = len(self.history)
        
        return result
    
    def get_full_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics from agent and memory."""
        metrics = self.memory.get_metrics()
        metrics['agent_steps'] = self.step_count
        metrics['history_items'] = len(self.history)
        return metrics
