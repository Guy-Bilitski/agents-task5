Task Specification: Experiment 3 - RAG vs. Full Context Analysis
Role: AI RAG Systems Engineer / Research Scientist Objective: Execute a comparative analysis between two information retrieval strategies: Full Context (Brute Force) vs. Retrieval-Augmented Generation (RAG). The goal is to demonstrate that RAG reduces "noise" and latency while improving accuracy.

Step 1: Dataset Preparation (Multi-Domain)
You are required to curate a corpus of 20 distinct documents in Hebrew.

Domain Diversity: The documents must cover three distinct fields to create semantic "noise":

Medicine (Target Domain)

Law (Distractor)

Technology (Distractor)

The "Needle" (Target Fact): Ensure one specific medical document contains the answer to the test query: "What are the side effects of Drug X?"

Distractors: The other 19 documents should contain unrelated information (e.g., contract laws, server specifications, other medical conditions).

Step 2: Infrastructure Setup (RAG Pipeline)
Before running the queries, establish the retrieval infrastructure:

Chunking: Split all 20 documents into segments of 500 tokens/characters.

Embedding: Generate vector embeddings for all chunks (using a model like Nomic or OpenAI).

Indexing: Ingest the embeddings into a Vector Store (e.g., ChromaDB).


Getty Images
Step 3: Execution Protocol (Comparison)
Perform the following two distinct retrieval modes using the query: "What are the side effects of Drug X?"

Mode A: Full Context (Baseline)
Context Construction: Concatenate ALL 20 documents into a single massive text block.

Execution: Feed this massive block into the LLM context window.

Measurement: Record the Latency (time to first token) and Accuracy (correctness/hallucination rate).

Hypothesis: High latency, high risk of "Lost in the Middle" or confusion due to noise.

Mode B: RAG (Experimental)
Retrieval: Perform a Similarity Search in the Vector Store using the query.

Filtering: Retrieve only the Top-3 (k=3) most relevant chunks.

Execution: Feed only these 3 chunks into the LLM context window.

Measurement: Record the Latency and Accuracy.

Hypothesis: Low latency, high accuracy.

Step 4: Final Output Requirement
Generate a comparative report containing:

Latency Comparison: Time taken for Mode A vs. Mode B.

Accuracy/Quality Check: Did Mode A get confused by the legal/tech documents? Did Mode B successfully isolate the medical fact?

Conclusion: Validate the expectation that RAG provides specific, accurate answers while Full Context suffers from noise and slowness.

Executable Python Workflow (Reference)
You can use this code as an optional reference made by gemini3:

Python

import time
import random

# Experiment Configuration
TOTAL_DOCS = 20
CHUNK_SIZE = 500
QUERY = "What are the side effects of Drug X?"
TARGET_FACT = "Drug X causes mild dizziness and dry mouth."

class MockVectorStore:
    def similarity_search(self, query, k=3):
        # Simulates finding the 1 relevant doc + 2 slightly related docs
        # In a real system, this uses cosine similarity
        return [
            f"Context: {TARGET_FACT} (Score: 0.95)",
            "Context: Drug Y is unrelated... (Score: 0.75)",
            "Context: Legal regulations for drugs... (Score: 0.70)"
        ]

def run_rag_experiment():
    print("--- Starting Experiment 3: RAG vs Full Context ---")
    
    # 1. Simulate Data Generation (20 docs x 500 words)
    # 1 Medical doc, 19 Distractors (Law/Tech)
    full_corpus_size = TOTAL_DOCS * 500 
    
    # --- MODE A: Full Context ---
    print("\n[Mode A] Executing Full Context Query...")
    start_time = time.time()
    
    # Simulate processing a massive context window
    # High latency penalty for processing 10,000 words
    time.sleep(2.0) 
    
    # Simulate "Lost in the Middle" / Noise interference
    # 30% chance of hallucination due to distractions
    mode_a_accuracy = random.choices([1, 0], weights=[0.7, 0.3])[0]
    mode_a_latency = time.time() - start_time
    
    print(f"Result A: Latency={mode_a_latency:.4f}s | Accuracy={'PASS' if mode_a_accuracy else 'FAIL (Noise)'}")

    # --- MODE B: RAG ---
    print("\n[Mode B] Executing RAG Query (k=3)...")
    vector_db = MockVectorStore()
    start_time = time.time()
    
    # 1. Retrieval (Fast)
    docs = vector_db.similarity_search(QUERY, k=3)
    
    # 2. Generation (Fast because context is small)
    time.sleep(0.5) 
    
    # High accuracy because noise was filtered out
    mode_b_accuracy = 1 
    mode_b_latency = time.time() - start_time
    
    print(f"Result B: Latency={mode_b_latency:.4f}s | Accuracy={'PASS' if mode_b_accuracy else 'FAIL'}")

    # --- Conclusion ---
    print("\n--- Final Analysis ---")
    print(f"Latency Reduction: {((mode_a_latency - mode_b_latency) / mode_a_latency) * 100:.1f}%")
    if mode_b_accuracy >= mode_a_accuracy:
        print("Conclusion: RAG strategy successfully filtered noise and improved efficiency.")
    else:
        print("Conclusion: Unexpected Result.")

run_rag_experiment()