Task Specification: Experiment 2 - Context Window Size Impact
Role: AI Research Scientist Objective: Execute a controlled experiment to evaluate the relationship between Context Window Size (input length) and model performance. The hypothesis is that as the context window grows (more documents), accuracy decreases and latency increases.

Step 1: Data Preparation & Scaling
You are required to configure an incremental test suite.

Scaling Factor: Define a progression of document counts to be tested: 2, 5, 10, 20, and 50 documents.

Context Construction: For each test level:

Load the specified number of documents.

Concatenate (merge) them into a single continuous text block to serve as the context.

Control Variable: Ensure the critical fact (the answer to the query) remains present in the text, while the amount of "noise" (filler text) increases.

Step 2: Execution Protocol
For each of the 5 scaling levels (2 to 50 documents), perform the following sequence:

Input: Feed the concatenated text into the target LLM.

Timing Start: Initiate a high-precision timer.

Query: Ask the specific question requiring information retrieval from the context.

Inference & Timing Stop: Record the response and stop the timer immediately upon completion.

Step 3: Metrics & Measurement
For every iteration, log the following data points:

Document Count: (e.g., 5).

Token Count: The total number of tokens in the prompt (Context + Query).

Latency: The total time taken for the inference (in seconds).

Accuracy: Evaluate the response (1 = Correct/Pass, 0 = Incorrect/Fail/Hallucination).

Step 4: Final Output Requirement
Generate a summary report containing:

A Performance Table correlating Document Count/Tokens with Latency and Accuracy.

A Visual Analysis (Graph): Plot "Context Size" (x-axis) vs. "Accuracy" (y-axis) to visualize the expected degradation curve.

Conclusion: specific observations regarding the "tipping point" where accuracy begins to fail.

Executable Python Workflow (Reference)
You can use this code as an optional reference made by gemini3:

Python

import time
import random

# Experiment Configuration
DOC_COUNTS = [2, 5, 10, 20, 50]
WORDS_PER_DOC = 200 # Approx 260 tokens per doc

def mock_llm_query(token_count):
    """
    Simulates LLM behavior:
    - Latency increases linearly with context length.
    - Accuracy degrades non-linearly as context gets very large.
    """
    # Simulate Latency (Processing time increases with input size)
    simulated_latency = 0.5 + (token_count * 0.0005) 
    time.sleep(simulated_latency * 0.1) # Reduced sleep for demo speed
    
    # Simulate Accuracy Drop (Probability of failure increases with size)
    # This represents the "Lost in the Middle" or "Context Saturation" effect
    if token_count > 10000:     # High load
        success_prob = 0.5
    elif token_count > 4000:    # Medium load
        success_prob = 0.8
    else:                       # Low load
        success_prob = 1.0
        
    accuracy = random.choices([1, 0], weights=[success_prob, 1-success_prob])[0]
    return accuracy, simulated_latency

def run_context_size_experiment():
    results = []
    print(f"--- Starting Experiment 2: Context Window Impact ---")
    print(f"{'Docs':<6} | {'Est. Tokens':<12} | {'Latency (s)':<12} | {'Accuracy':<10}")
    print("-" * 50)
    
    for count in DOC_COUNTS:
        # 1. Prepare Data
        total_words = count * WORDS_PER_DOC
        est_tokens = int(total_words * 1.3) # Rough approximation
        
        # 2. Execution
        start_time = time.time()
        # In a real scenario, this is where the actual LLM API call happens:
        accuracy, sim_latency = mock_llm_query(est_tokens) 
        
        # 3. Logging
        results.append({
            'num_docs': count,
            'tokens': est_tokens,
            'latency': round(sim_latency, 3),
            'accuracy': accuracy
        })
        
        status = "PASS" if accuracy == 1 else "FAIL"
        print(f"{count:<6} | {est_tokens:<12} | {sim_latency:<12.3f} | {status:<10}")

    # 4. Final Report Logic
    print("\n--- Conclusion ---")
    failures = [r for r in results if r['accuracy'] == 0]
    if failures:
        print(f"Accuracy degradation observed starting at ~{failures[0]['tokens']} tokens.")
    else:
        print("No accuracy degradation observed within this range.")

# Execute
run_context_size_experiment()