Task Specification: "Lost in the Middle" Phenomenon Simulation
Role: AI Research Scientist Objective: Execute a controlled experiment to evaluate the "Lost in the Middle" phenomenon—the hypothesis that Large Language Models (LLMs) retrieve information more accurately from the start or end of a context window than from the middle.

Step 1: Dataset Generation (Synthesis)
You are required to generate a synthetic dataset consisting of 5 distinct documents. Follow these parameters for each document:

Context Length: Generate approximately 200 words of coherent but irrelevant filler text (e.g., descriptions of weather, history of unrelated objects, or lorem ipsum-style narrative).

The "Needle" (Critical Fact): Define a specific, arbitrary fact.

Example: "Uncle Cohen is the CEO of the company."

Variable Injection: Embed this critical fact into the filler text. You must vary the position of this fact across the 5 documents to ensure coverage:

Start: First 10% of the text.

Middle: 45%–55% mark of the text.

End: Last 10% of the text.

Step 2: Execution Protocol
For each of the 5 generated documents, perform the following:

Input: Feed the full document (filler + embedded fact) into the target LLM as the "Context".

Query: Ask the LLM a specific question that requires retrieving the embedded fact.

Query Example: "Who is the CEO of the company?"

Inference: Record the LLM's generated response.

Step 3: Evaluation & Analysis
Verification: Compare the LLM's response against the Ground Truth (e.g., "Uncle Cohen").

Scoring: Assign a binary score (1 for Pass, 0 for Fail) for each attempt.

Aggregation: Group the results by the position of the fact (Start vs. Middle vs. End).

Step 4: Final Output Requirement
Generate a summary report containing:

The generated text samples (optional/snippet).

A performance table showing accuracy per position.

Conclusion: Confirm if the results align with the hypothesis (High accuracy at Start/End, Lower accuracy at Middle).

Executable Python Workflow (Reference)
You can use this code as an optional reference made by gemini3:

Python

import random

# Configuration
NUM_DOCS = 5
DOC_LENGTH_WORDS = 200
CRITICAL_FACT = "Uncle Cohen is the CEO of the company."
QUERY = "Who is the CEO of the company?"
EXPECTED_ANSWER = "Uncle Cohen"

def generate_text_with_fact(position):
    # Generate generic filler words
    filler = ["word" + str(i) for i in range(DOC_LENGTH_WORDS)]
    
    fact_tokens = CRITICAL_FACT.split()
    
    if position == 'start':
        insert_idx = 0
    elif position == 'end':
        insert_idx = len(filler)
    else: # middle
        insert_idx = len(filler) // 2
        
    # Insert fact
    document_tokens = filler[:insert_idx] + fact_tokens + filler[insert_idx:]
    return " ".join(document_tokens)

def run_experiment():
    results = {'start': [], 'middle': [], 'end': []}
    positions = ['start', 'middle', 'middle', 'middle', 'end'] # Ensure middle is tested well
    
    print(f"--- Starting Experiment: {NUM_DOCS} Documents ---")
    
    for pos in positions:
        # 1. Generate
        doc_text = generate_text_with_fact(pos)
        
        # 2. Query (Mocking an LLM call here)
        # In real scenario: response = llm.invoke(f"Context: {doc_text}\n\nQuestion: {QUERY}")
        # For simulation, we assume standard Lost-in-Middle behavior:
        if pos == 'middle':
            simulated_accuracy = random.choice([0, 1]) # Lower probability
        else:
            simulated_accuracy = 1 # High probability
            
        results[pos].append(simulated_accuracy)
        print(f"Tested Position: {pos} | Accuracy: {simulated_accuracy}")

    # 3. Report
    print("\n--- Final Results ---")
    for pos, scores in results.items():
        avg = sum(scores) / len(scores) if scores else 0
        print(f"{pos.capitalize()}: {avg*100}% Accuracy")

run_experiment()