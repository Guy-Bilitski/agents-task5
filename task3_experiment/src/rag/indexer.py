"""RAG System components (Indexer & Retriever)."""

import math
import re
from typing import List, Dict, Tuple, Set, Any
from dataclasses import dataclass

@dataclass
class Chunk:
    id: str
    doc_id: int
    text: str
    metadata: Dict[str, Any]

class SimpleTokenizer:
    """Basic tokenizer for Hebrew/English."""
    @staticmethod
    def tokenize(text: str) -> List[str]:
        # Simple regex to split by whitespace and remove punctuation
        # Hebrew unicode range \u0590-\u05FF
        # Keeping it simple: alphanumeric + hebrew chars
        tokens = re.findall(r'[\w\u0590-\u05FF]+', text.lower())
        return tokens

class VectorStore:
    """A lightweight TF-IDF based vector store implementation."""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chunks: List[Chunk] = []
        
        # Inverted index: word -> List[(chunk_index, tf_score)]
        self.inverted_index: Dict[str, List[Tuple[int, float]]] = {}
        # Document frequencies: word -> count of chunks containing it
        self.doc_freqs: Dict[str, int] = {}
        self.total_chunks = 0
        
    def add_documents(self, documents: List[Any]):
        """Chunk and index documents."""
        self.chunks = []
        chunk_counter = 0
        
        for doc in documents:
            doc_chunks = self._create_chunks(doc)
            for chunk_text in doc_chunks:
                chunk = Chunk(
                    id=f"chunk_{chunk_counter}",
                    doc_id=doc.id,
                    text=chunk_text,
                    metadata={"domain": doc.domain, "has_needle": doc.has_needle}
                )
                self.chunks.append(chunk)
                chunk_counter += 1
                
        self.total_chunks = len(self.chunks)
        self._build_index()
        
    def _create_chunks(self, doc: Any) -> List[str]:
        """Split document text into chunks."""
        words = doc.text.split() # Simple space splitting
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i : i + self.chunk_size]
            
            # Avoid creating a tiny chunk at the end if it's mostly overlap
            # If this is not the first chunk, and it's shorter than overlap + epsilon, skip it
            # because it's largely contained in the previous chunk.
            if i > 0 and len(chunk_words) <= self.overlap:
                continue
                
            chunks.append(" ".join(chunk_words))
            
        return chunks
        
    def _build_index(self):
        """Calculate TF-IDF and build inverted index."""
        self.inverted_index = {}
        self.doc_freqs = {}
        
        # 1. Calculate Document Frequencies (DF)
        for i, chunk in enumerate(self.chunks):
            tokens = set(SimpleTokenizer.tokenize(chunk.text))
            for token in tokens:
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1
                
        # 2. Calculate TF and populate Inverted Index
        for i, chunk in enumerate(self.chunks):
            tokens = SimpleTokenizer.tokenize(chunk.text)
            if not tokens:
                continue
                
            term_counts = {}
            for token in tokens:
                term_counts[token] = term_counts.get(token, 0) + 1
            
            total_terms = len(tokens)
            
            for token, count in term_counts.items():
                tf = count / total_terms
                if token not in self.inverted_index:
                    self.inverted_index[token] = []
                self.inverted_index[token].append((i, tf))
                
    def similarity_search(self, query: str, k: int = 3) -> List[Chunk]:
        """Retrieve top-k chunks based on TF-IDF score."""
        query_tokens = SimpleTokenizer.tokenize(query)
        
        # Chunk Index -> Accumulator Score
        scores: Dict[int, float] = {}
        
        for token in query_tokens:
            if token in self.inverted_index:
                # IDF = log(Total Documents / Document Frequency)
                df = self.doc_freqs.get(token, 0)
                idf = math.log(1 + (self.total_chunks / (1 + df)))
                
                # Add TF * IDF to accumulator
                for chunk_idx, tf in self.inverted_index[token]:
                    scores[chunk_idx] = scores.get(chunk_idx, 0.0) + (tf * idf)
                    
        # Sort by score descending
        sorted_chunks = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        
        # Return top k
        top_indices = [idx for idx, score in sorted_chunks[:k]]
        return [self.chunks[i] for i in top_indices]

