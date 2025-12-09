"""Professional RAG System using FAISS and Sentence Transformers."""

import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer

@dataclass
class Chunk:
    id: str
    doc_id: int
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None

class VectorStore:
    """Production-grade FAISS-based vector store with dense embeddings."""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50, 
                 embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize FAISS vector store.
        
        Args:
            chunk_size: Number of words per chunk
            overlap: Number of overlapping words between chunks
            embedding_model: SentenceTransformer model name (multilingual for Hebrew support)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chunks: List[Chunk] = []
        
        # Load embedding model (multilingual for Hebrew support)
        print(f"Loading embedding model: {embedding_model}")
        self.encoder = SentenceTransformer(embedding_model)
        self.embedding_dim = self.encoder.get_sentence_embedding_dimension()
        
        # FAISS index (L2 distance, can switch to cosine similarity)
        self.index: Optional[faiss.IndexFlatL2] = None
        self.total_chunks = 0
        
    def add_documents(self, documents: List[Any]):
        """Chunk documents, generate embeddings, and index with FAISS."""
        self.chunks = []
        chunk_counter = 0
        
        # 1. Create chunks
        print("Chunking documents...")
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
        print(f"Created {self.total_chunks} chunks")
        
        # 2. Generate embeddings
        print("Generating embeddings...")
        chunk_texts = [chunk.text for chunk in self.chunks]
        embeddings = self.encoder.encode(chunk_texts, show_progress_bar=True, 
                                         convert_to_numpy=True, batch_size=32)
        
        # Store embeddings in chunks
        for i, chunk in enumerate(self.chunks):
            chunk.embedding = embeddings[i]
        
        # 3. Build FAISS index
        print("Building FAISS index...")
        self._build_faiss_index(embeddings)
        print("Indexing complete!")
        
    def _create_chunks(self, doc: Any) -> List[str]:
        """Split document text into overlapping chunks."""
        words = doc.text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i : i + self.chunk_size]
            
            if i > 0 and len(chunk_words) <= self.overlap:
                continue
                
            chunks.append(" ".join(chunk_words))
            
        return chunks
        
    def _build_faiss_index(self, embeddings: np.ndarray):
        """Build FAISS index for efficient similarity search."""
        # Use L2 distance (Euclidean)
        # For cosine similarity, normalize embeddings first
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add vectors to index
        self.index.add(embeddings.astype('float32'))
        
    def similarity_search(self, query: str, k: int = 3) -> List[Chunk]:
        """
        Retrieve top-k most similar chunks using FAISS semantic search.
        
        Args:
            query: Search query
            k: Number of top results to return
            
        Returns:
            List of top-k most relevant chunks
        """
        if self.index is None or self.total_chunks == 0:
            return []
        
        # Encode query
        query_embedding = self.encoder.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Return corresponding chunks
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.chunks):
                results.append(self.chunks[idx])
        
        return results

