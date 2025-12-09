"""Task 4: Strategies Implementation."""

from typing import List, Dict, Any
import string

class ContextStrategies:

    @staticmethod
    def select_strategy(history: List[str], query: str, top_k: int = 2) -> str:
        """
        Strategy A: SELECT (RAG-based).
        Retrieves top_k most relevant lines based on keyword matching.
        """
        # Simple keyword matching simulation of RAG
        # Strip punctuation from query words for proper matching
        query_words = set(word.strip(string.punctuation).lower() for word in query.split())
        scored_lines = []
        
        for line in history:
            score = sum(1 for word in query_words if word in line.lower())
            scored_lines.append((score, line))
            
        # Sort by score desc
        scored_lines.sort(key=lambda x: x[0], reverse=True)
        
        # Take top k
        selected = [line for score, line in scored_lines[:top_k]]
        
        # If no matches, take recent (fallback)
        if not selected or all(s[0] == 0 for s in scored_lines[:top_k]):
             selected = history[-top_k:]
             
        return "\n".join(selected)

    @staticmethod
    def compress_strategy(history: List[str], max_tokens: int = 100) -> str:
        """
        Strategy B: COMPRESS (Summarization).
        Summarizes old history if it exceeds limit.
        """
        full_text = "\n".join(history)
        
        # Heuristic: 1 word ~ 1 token (simple)
        if len(full_text.split()) <= max_tokens:
            return full_text
            
        # Mock Summarization Logic
        # In real world: LLM call to summarize history[:-3]
        summary = "Summary: User explored a dungeon, found items, and met Steve."
        recent = "\n".join(history[-3:])
        
        return f"{summary}\n[...skipped...]\n{recent}"

    @staticmethod
    def write_strategy(history_step: str, scratchpad: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Strategy C: WRITE (Scratchpad).
        Updates structured memory based on new event.
        """
        # Rule-based extraction simulation
        lower_step = history_step.lower()
        
        if "key" in lower_step:
            # Extract color if present
            color = "Unknown"
            if "blue" in lower_step: color = "Blue"
            elif "red" in lower_step: color = "Red"
            scratchpad['inventory'].append(f"{color} Key")
            
        if "steve" in lower_step:
            if "Steve" not in scratchpad['npcs']:
                scratchpad['npcs'].append("Steve")
                
        if "password" in lower_step:
            # Extract password (mock)
            if "shadow" in lower_step:
                scratchpad['knowledge'].append("Password: Shadow")
                
        return scratchpad
