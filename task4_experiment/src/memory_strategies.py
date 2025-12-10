"""Real memory management strategies using LLM."""

import time
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from task4_experiment.src.agent import MemoryStrategy


class SelectStrategy(MemoryStrategy):
    """SELECT: RAG-based semantic retrieval of relevant history."""
    
    def __init__(self, top_k: int = 3, embedding_model: str = "all-MiniLM-L6-v2"):
        self.history = []
        self.embeddings = []
        self.top_k = top_k
        self.encoder = SentenceTransformer(embedding_model)
        self.llm_calls = 0
        self.total_latency = 0.0
        self.total_tokens = 0
        
    def process_step(self, step: str, llm, **kwargs) -> None:
        """Store step and compute embedding."""
        self.history.append(step)
        embedding = self.encoder.encode(step, convert_to_numpy=True)
        self.embeddings.append(embedding)
        
        logger = kwargs.get('logger')
        if logger:
            logger.debug(f"SELECT: Stored step {len(self.history)}")
    
    def query(self, question: str, llm, **kwargs) -> Dict[str, Any]:
        """Retrieve relevant steps and query LLM."""
        start_time = time.time()
        
        logger = kwargs.get('logger')
        
        # 1. Encode question
        question_embedding = self.encoder.encode(question, convert_to_numpy=True)
        
        # 2. Compute similarities
        similarities = []
        for emb in self.embeddings:
            sim = np.dot(question_embedding, emb) / (
                np.linalg.norm(question_embedding) * np.linalg.norm(emb)
            )
            similarities.append(sim)
        
        # 3. Get top-k indices
        top_indices = np.argsort(similarities)[-self.top_k:][::-1]
        relevant_steps = [self.history[i] for i in top_indices]
        
        if logger:
            logger.info(f"SELECT: Retrieved {len(relevant_steps)} relevant steps (indices: {top_indices.tolist()})")
        
        # 4. Build context
        context = "Based on the following relevant events:\n" + "\n".join(
            [f"- {step}" for step in relevant_steps]
        )
        
        # 5. Query LLM
        result = llm.query(
            context=context,
            question=question,
            expected_answer=kwargs.get('expected_answer', '')
        )
        
        self.llm_calls += 1
        self.total_latency = time.time() - start_time
        self.total_tokens += result.get('token_count', 0)
        
        result['strategy'] = 'SELECT'
        result['retrieved_steps'] = len(relevant_steps)
        result['context_used'] = context
        
        return result
    
    def get_metrics(self) -> Dict[str, Any]:
        return {
            'strategy': 'SELECT',
            'llm_calls': self.llm_calls,
            'total_latency': self.total_latency,
            'total_tokens': self.total_tokens,
            'history_size': len(self.history)
        }


class CompressStrategy(MemoryStrategy):
    """COMPRESS: Periodically summarize history using LLM."""
    
    def __init__(self, compression_interval: int = 3, max_recent: int = 2):
        self.full_history = []
        self.compressed_summary = ""
        self.recent_history = []
        self.compression_interval = compression_interval
        self.max_recent = max_recent
        self.llm_calls = 0
        self.total_latency = 0.0
        self.total_tokens = 0
        self.compression_count = 0
        
    def process_step(self, step: str, llm, **kwargs) -> None:
        """Add step and compress if needed."""
        start_time = time.time()
        
        self.full_history.append(step)
        self.recent_history.append(step)
        
        logger = kwargs.get('logger')
        
        # Check if we need to compress
        if len(self.recent_history) >= self.compression_interval:
            # Compress older items
            to_compress = self.recent_history[:-self.max_recent]
            
            if to_compress:
                # Use LLM to summarize
                context = "Summarize the following sequence of events into a brief summary:\n" + "\n".join(
                    [f"{i+1}. {event}" for i, event in enumerate(to_compress)]
                )
                
                result = llm.query(
                    context=context,
                    question="Provide a concise summary (1-2 sentences) of these events.",
                    expected_answer=""
                )
                
                new_summary = result['response']
                
                # Append to existing summary
                if self.compressed_summary:
                    self.compressed_summary += " " + new_summary
                else:
                    self.compressed_summary = new_summary
                
                # Keep only recent items
                self.recent_history = self.recent_history[-self.max_recent:]
                
                self.llm_calls += 1
                self.compression_count += 1
                self.total_tokens += result.get('token_count', 0)
                
                if logger:
                    logger.info(f"COMPRESS: Compressed {len(to_compress)} steps. Compression #{self.compression_count}")
                    logger.debug(f"Summary: {new_summary}")
        
        self.total_latency += (time.time() - start_time)
    
    def query(self, question: str, llm, **kwargs) -> Dict[str, Any]:
        """Query using compressed summary + recent history."""
        start_time = time.time()
        
        logger = kwargs.get('logger')
        
        # Build context from summary + recent
        context_parts = []
        if self.compressed_summary:
            context_parts.append(f"Summary of earlier events: {self.compressed_summary}")
        
        if self.recent_history:
            context_parts.append("Recent events:")
            context_parts.extend([f"- {event}" for event in self.recent_history])
        
        context = "\n".join(context_parts)
        
        if logger:
            logger.info(f"COMPRESS: Querying with summary ({len(self.compressed_summary)} chars) + {len(self.recent_history)} recent events")
        
        # Query LLM
        result = llm.query(
            context=context,
            question=question,
            expected_answer=kwargs.get('expected_answer', '')
        )
        
        self.llm_calls += 1
        query_time = time.time() - start_time
        self.total_latency += query_time
        self.total_tokens += result.get('token_count', 0)
        
        result['strategy'] = 'COMPRESS'
        result['compressions_performed'] = self.compression_count
        result['context_used'] = context
        
        return result
    
    def get_metrics(self) -> Dict[str, Any]:
        return {
            'strategy': 'COMPRESS',
            'llm_calls': self.llm_calls,
            'total_latency': self.total_latency,
            'total_tokens': self.total_tokens,
            'compressions': self.compression_count,
            'summary_length': len(self.compressed_summary),
            'recent_items': len(self.recent_history)
        }


class WriteStrategy(MemoryStrategy):
    """WRITE: Maintain structured scratchpad using LLM extraction."""
    
    def __init__(self):
        self.scratchpad = {
            'inventory': [],
            'npcs': [],
            'knowledge': [],
            'locations': []
        }
        self.llm_calls = 0
        self.total_latency = 0.0
        self.total_tokens = 0
        
    def process_step(self, step: str, llm, **kwargs) -> None:
        """Use LLM to extract structured information."""
        start_time = time.time()
        
        logger = kwargs.get('logger')
        
        # Build extraction prompt
        context = f"""Current scratchpad state:
Inventory: {', '.join(self.scratchpad['inventory']) if self.scratchpad['inventory'] else 'empty'}
NPCs: {', '.join(self.scratchpad['npcs']) if self.scratchpad['npcs'] else 'none'}
Knowledge: {', '.join(self.scratchpad['knowledge']) if self.scratchpad['knowledge'] else 'none'}
Locations: {', '.join(self.scratchpad['locations']) if self.scratchpad['locations'] else 'none'}

New event: {step}

Extract any new items, NPCs, knowledge, or locations from this event. Respond with:
- INVENTORY: [item with description if any]
- NPC: [name if any]
- KNOWLEDGE: [fact if any]
- LOCATION: [place if any]
Respond "NONE" for categories with no new information."""

        result = llm.query(
            context=context,
            question="Extract structured information from the event.",
            expected_answer=""
        )
        
        response = result['response'].lower()
        
        # Parse response (simple extraction)
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if 'inventory:' in line and 'none' not in line:
                item = line.split('inventory:', 1)[1].strip()
                if item and item not in self.scratchpad['inventory']:
                    self.scratchpad['inventory'].append(item)
            elif 'npc:' in line and 'none' not in line:
                npc = line.split('npc:', 1)[1].strip()
                if npc and npc not in self.scratchpad['npcs']:
                    self.scratchpad['npcs'].append(npc)
            elif 'knowledge:' in line and 'none' not in line:
                knowledge = line.split('knowledge:', 1)[1].strip()
                if knowledge and knowledge not in self.scratchpad['knowledge']:
                    self.scratchpad['knowledge'].append(knowledge)
            elif 'location:' in line and 'none' not in line:
                location = line.split('location:', 1)[1].strip()
                if location and location not in self.scratchpad['locations']:
                    self.scratchpad['locations'].append(location)
        
        self.llm_calls += 1
        self.total_latency += (time.time() - start_time)
        self.total_tokens += result.get('token_count', 0)
        
        if logger:
            logger.debug(f"WRITE: Processed step. Scratchpad now has {sum(len(v) for v in self.scratchpad.values())} items")
    
    def query(self, question: str, llm, **kwargs) -> Dict[str, Any]:
        """Query using structured scratchpad."""
        start_time = time.time()
        
        logger = kwargs.get('logger')
        
        # Build context from scratchpad
        context = "Agent's Memory Scratchpad:\n"
        context += f"Inventory: {', '.join(self.scratchpad['inventory']) if self.scratchpad['inventory'] else 'empty'}\n"
        context += f"NPCs Met: {', '.join(self.scratchpad['npcs']) if self.scratchpad['npcs'] else 'none'}\n"
        context += f"Knowledge: {', '.join(self.scratchpad['knowledge']) if self.scratchpad['knowledge'] else 'none'}\n"
        context += f"Locations: {', '.join(self.scratchpad['locations']) if self.scratchpad['locations'] else 'none'}\n"
        
        if logger:
            logger.info(f"WRITE: Querying with scratchpad ({sum(len(v) for v in self.scratchpad.values())} total items)")
        
        # Query LLM
        result = llm.query(
            context=context,
            question=question,
            expected_answer=kwargs.get('expected_answer', '')
        )
        
        self.llm_calls += 1
        query_time = time.time() - start_time
        self.total_latency += query_time
        self.total_tokens += result.get('token_count', 0)
        
        result['strategy'] = 'WRITE'
        result['scratchpad_items'] = sum(len(v) for v in self.scratchpad.values())
        result['context_used'] = context
        
        return result
    
    def get_metrics(self) -> Dict[str, Any]:
        return {
            'strategy': 'WRITE',
            'llm_calls': self.llm_calls,
            'total_latency': self.total_latency,
            'total_tokens': self.total_tokens,
            'scratchpad_items': sum(len(v) for v in self.scratchpad.values())
        }
