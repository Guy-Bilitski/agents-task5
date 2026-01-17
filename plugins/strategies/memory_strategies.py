"""
Memory Strategy Plugins.

This module provides pluggable memory management strategies for multi-step
agent experiments. Each strategy implements a different approach to managing
context within token limits.

Available Strategies:
    - SelectStrategy: RAG-based retrieval of relevant history
    - CompressStrategy: Summarization of context
    - WriteStrategy: Scratchpad-based persistence
    - SlidingWindowStrategy: Fixed-size sliding window

Usage:
    from common.plugins import strategy_registry

    strategy = strategy_registry.create_instance("select", top_k=3)
    processed = strategy.process(context, query, history)
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common.plugins import BaseStrategyPlugin, plugin


@plugin(name="select", metadata={
    "description": "RAG-based selection of relevant context",
    "version": "1.0.0"
})
class SelectStrategy(BaseStrategyPlugin):
    """
    SELECT strategy using RAG-based retrieval.

    Selects the most relevant portions of history based on semantic
    similarity to the current query. Uses simple keyword matching
    as a lightweight alternative to vector similarity.
    """

    PLUGIN_NAME = "select"

    def __init__(self, top_k: int = 3, similarity_threshold: float = 0.1):
        """
        Initialize SELECT strategy.

        Args:
            top_k: Number of history items to select
            similarity_threshold: Minimum similarity to include
        """
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self._total_tokens = 0
        self._retrieved_count = 0

    def process(self, context: str, query: str, history: List[str]) -> str:
        """
        Select relevant history items based on query.

        Args:
            context: Current context
            query: Current query
            history: Conversation history

        Returns:
            Context with selected history items
        """
        if not history:
            self._total_tokens = len(context.split())
            return context

        # Simple keyword-based relevance scoring
        query_words = set(query.lower().split())
        scored_history = []

        for item in history:
            item_words = set(item.lower().split())
            overlap = len(query_words & item_words)
            score = overlap / max(len(query_words), 1)
            if score >= self.similarity_threshold:
                scored_history.append((score, item))

        # Sort by relevance and select top_k
        scored_history.sort(reverse=True, key=lambda x: x[0])
        selected = [item for _, item in scored_history[:self.top_k]]

        self._retrieved_count = len(selected)

        # Combine selected history with current context
        if selected:
            selected_text = "\n".join(selected)
            result = f"Relevant history:\n{selected_text}\n\nCurrent context:\n{context}"
        else:
            result = context

        self._total_tokens = len(result.split())
        return result

    def get_metrics(self) -> Dict[str, Any]:
        """Get strategy metrics."""
        return {
            "strategy": "select",
            "total_tokens": self._total_tokens,
            "retrieved_count": self._retrieved_count,
            "top_k": self.top_k
        }


@plugin(name="compress", metadata={
    "description": "Context compression via summarization",
    "version": "1.0.0"
})
class CompressStrategy(BaseStrategyPlugin):
    """
    COMPRESS strategy using summarization.

    Compresses history by extracting key information and removing
    redundancy. Uses extractive summarization by default.
    """

    PLUGIN_NAME = "compress"

    def __init__(self, max_tokens: int = 500, compression_ratio: float = 0.3):
        """
        Initialize COMPRESS strategy.

        Args:
            max_tokens: Maximum tokens in compressed output
            compression_ratio: Target compression ratio
        """
        self.max_tokens = max_tokens
        self.compression_ratio = compression_ratio
        self._original_tokens = 0
        self._compressed_tokens = 0

    def process(self, context: str, query: str, history: List[str]) -> str:
        """
        Compress history and context.

        Args:
            context: Current context
            query: Current query
            history: Conversation history

        Returns:
            Compressed context
        """
        # Combine all text
        full_text = " ".join(history) + " " + context if history else context
        self._original_tokens = len(full_text.split())

        # Simple extractive compression: keep sentences with key terms
        sentences = self._split_sentences(full_text)
        query_words = set(query.lower().split())

        # Score sentences by relevance
        scored = []
        for sent in sentences:
            sent_words = set(sent.lower().split())
            score = len(query_words & sent_words)
            scored.append((score, sent))

        # Sort and select top sentences within token limit
        scored.sort(reverse=True, key=lambda x: x[0])

        compressed = []
        token_count = 0
        for _, sent in scored:
            sent_tokens = len(sent.split())
            if token_count + sent_tokens <= self.max_tokens:
                compressed.append(sent)
                token_count += sent_tokens

        result = " ".join(compressed) if compressed else context[:self.max_tokens * 4]
        self._compressed_tokens = len(result.split())

        return result

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def get_metrics(self) -> Dict[str, Any]:
        """Get strategy metrics."""
        ratio = self._compressed_tokens / max(self._original_tokens, 1)
        return {
            "strategy": "compress",
            "original_tokens": self._original_tokens,
            "compressed_tokens": self._compressed_tokens,
            "actual_compression_ratio": ratio,
            "target_compression_ratio": self.compression_ratio
        }


@plugin(name="write", metadata={
    "description": "Scratchpad-based memory persistence",
    "version": "1.0.0"
})
class WriteStrategy(BaseStrategyPlugin):
    """
    WRITE strategy using a persistent scratchpad.

    Maintains a scratchpad of key information that persists across
    steps. New information is written to the scratchpad, and queries
    can reference it.
    """

    PLUGIN_NAME = "write"

    def __init__(self, max_scratchpad_size: int = 200):
        """
        Initialize WRITE strategy.

        Args:
            max_scratchpad_size: Maximum tokens in scratchpad
        """
        self.max_scratchpad_size = max_scratchpad_size
        self.scratchpad: Dict[str, str] = {}
        self._total_tokens = 0
        self._write_count = 0

    def process(self, context: str, query: str, history: List[str]) -> str:
        """
        Process context using scratchpad.

        Args:
            context: Current context (may contain WRITE commands)
            query: Current query
            history: Conversation history

        Returns:
            Context with scratchpad contents
        """
        # Extract and process WRITE commands from context
        self._extract_writes(context)

        # Build scratchpad representation
        scratchpad_text = self._format_scratchpad()

        # Combine with current context
        if scratchpad_text:
            result = f"Scratchpad:\n{scratchpad_text}\n\nCurrent:\n{context}"
        else:
            result = context

        self._total_tokens = len(result.split())
        return result

    def _extract_writes(self, text: str) -> None:
        """Extract WRITE commands from text."""
        import re
        # Look for patterns like "WRITE key: value" or "Remember: key = value"
        patterns = [
            r'WRITE\s+(\w+):\s*(.+?)(?:\.|$)',
            r'Remember:\s*(\w+)\s*=\s*(.+?)(?:\.|$)',
            r'Note:\s*(\w+)\s*is\s*(.+?)(?:\.|$)'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for key, value in matches:
                self.scratchpad[key.lower()] = value.strip()
                self._write_count += 1

    def _format_scratchpad(self) -> str:
        """Format scratchpad for inclusion in context."""
        if not self.scratchpad:
            return ""

        lines = [f"- {key}: {value}" for key, value in self.scratchpad.items()]
        return "\n".join(lines)

    def write(self, key: str, value: str) -> None:
        """Explicitly write to scratchpad."""
        self.scratchpad[key.lower()] = value
        self._write_count += 1

    def read(self, key: str) -> str:
        """Read from scratchpad."""
        return self.scratchpad.get(key.lower(), "")

    def clear(self) -> None:
        """Clear the scratchpad."""
        self.scratchpad.clear()

    def get_metrics(self) -> Dict[str, Any]:
        """Get strategy metrics."""
        return {
            "strategy": "write",
            "total_tokens": self._total_tokens,
            "scratchpad_entries": len(self.scratchpad),
            "write_operations": self._write_count,
            "max_size": self.max_scratchpad_size
        }


@plugin(name="sliding_window", metadata={
    "description": "Fixed-size sliding window over history",
    "version": "1.0.0"
})
class SlidingWindowStrategy(BaseStrategyPlugin):
    """
    Sliding window strategy.

    Maintains a fixed-size window over the most recent history items.
    Simple but effective for many use cases.
    """

    PLUGIN_NAME = "sliding_window"

    def __init__(self, window_size: int = 5, max_tokens: int = 1000):
        """
        Initialize sliding window strategy.

        Args:
            window_size: Number of history items to keep
            max_tokens: Maximum tokens in output
        """
        self.window_size = window_size
        self.max_tokens = max_tokens
        self._total_tokens = 0
        self._items_included = 0

    def process(self, context: str, query: str, history: List[str]) -> str:
        """
        Apply sliding window to history.

        Args:
            context: Current context
            query: Current query
            history: Conversation history

        Returns:
            Context with windowed history
        """
        # Take most recent items
        window = history[-self.window_size:] if history else []
        self._items_included = len(window)

        # Combine with current context
        if window:
            window_text = "\n".join(window)
            result = f"Recent history:\n{window_text}\n\nCurrent:\n{context}"
        else:
            result = context

        # Truncate if necessary
        words = result.split()
        if len(words) > self.max_tokens:
            result = " ".join(words[:self.max_tokens])

        self._total_tokens = len(result.split())
        return result

    def get_metrics(self) -> Dict[str, Any]:
        """Get strategy metrics."""
        return {
            "strategy": "sliding_window",
            "total_tokens": self._total_tokens,
            "items_included": self._items_included,
            "window_size": self.window_size,
            "max_tokens": self.max_tokens
        }
