Task Specification: Experiment 4 - Context Engineering StrategiesRole: AI Systems Architect / Prompt EngineerObjective: Evaluate and benchmark different Context Management Strategies (Memory Architectures) for Long-Horizon Agentic Tasks. The goal is to determine which method best maintains accuracy and reduces token usage over a sequence of sequential actions.Experiment Strategies to Test: Select (RAG), Compress (Summarization), Write (External Memory/Scratchpad).Step 1: Environment Setup (Sequential Task Simulation)You must simulate an agent performing a multi-step task consisting of 10 sequential actions.The Workflow: At every step, the agent performs an action (e.g., "Step 1: Found a key," "Step 2: Opened the door," "Step 3: Met a wizard...").The Accumulation: Each step produces a text Output. Normally, these outputs are appended to a growing History list.The Challenge: By Step 10, the context is noisy. The agent must answer a query regarding an early step (e.g., "What color was the key found in Step 1?").Step 2: Strategy ImplementationYou must implement and test three distinct context management strategies to handle this growing history:Strategy A: SELECT (RAG-based)Mechanism: Do not feed the full history to the LLM.Action: When a query is posed, use Semantic Search (Vector Database) to retrieve only the top $k$ (e.g., $k=5$) most relevant historical log entries.Hypothesis: High accuracy for specific facts, low token usage.Strategy B: COMPRESS (Summarization)Mechanism: Maintain a rolling window of raw text.Action: If the history exceeds a defined token limit (e.g., MAX_TOKENS), trigger a summarization call to condense the oldest history into a concise abstract, keeping only the most recent steps raw.Hypothesis: Good for general narrative flow, risk of losing specific details ("lossy compression").Strategy C: WRITE (External Memory / Scratchpad)Mechanism: Maintain a separate, structured "Scratchpad" or "Knowledge Graph."Action: After every step, an auxiliary LLM call extracts Key Facts (Entities, Attributes, State Changes) and writes them to the Scratchpad. The context fed to the agent is only the Scratchpad, not the raw history.Hypothesis: Highly efficient for state tracking, requires complex setup.Step 3: Execution Protocol (Benchmarking)Iterate: Run the simulation from Step 1 to Step 10.Query: At specific intervals (e.g., after Step 5 and Step 10), pose a retrieval query about a previous state.Evaluate: For each strategy, measure:Accuracy: Did it retrieve the correct detail?Token Consumption: How many tokens were fed to the LLM?Information Loss: Did the strategy delete the required fact?Step 4: Final Output RequirementGenerate a technical report containing:Comparative Table: Columns for Strategy, Token Usage, and Accuracy Score.Trade-off Analysis: When should "Compress" be used over "Select"?Conclusion: Which strategy is best for long-context agents?Executable Python Workflow (Reference)
You can use this code as an optional reference made by gemini3:

# Experiment Configuration
NUM_ACTIONS = 10
MAX_TOKENS_LIMIT = 500  # Threshold for 'Compress' strategy

# Simulated History Generator
def generate_action_output(step):
    actions = [
        "Found a Blue Key under the mat.",
        "Unlocked the heavy Oak Door.",
        "Entered the hallway and saw a Red Painting.",
        "Spoke to the Guard named Steve.",
        "Steve asked for a password.",
        "Found a note saying the password is 'Shadow'.",
        "Gave password to Steve.",
        "Steve opened the Gate.",
        "Entered the Garden.",
        "Found the Treasure Chest."
    ]
    return f"Step {step+1}: {actions[step]}"

# --- Strategy Definitions ---

def strategy_select(history, query):
    # Simulates RAG: keyword matching to find relevant lines
    # In real world: Vector Search
    relevant_chunks = [line for line in history if any(word in line for word in query.split())]
    if not relevant_chunks:
        relevant_chunks = history[-2:] # Fallback to recent
    return "\n".join(relevant_chunks)

def strategy_compress(history):
    # Simulates Summarization: If too long, keep first summary + last 3 steps
    full_text = "\n".join(history)
    if len(full_text) > MAX_TOKENS_LIMIT:
        summary = "Summary: User found keys, passed guard Steve, entered garden."
        recent = "\n".join(history[-3:])
        return f"{summary}\n...\n{recent}"
    return full_text

def strategy_write(scratchpad, new_log):
    # Simulates updating a structured state object
    # In real world: LLM extraction
    if "Blue Key" in new_log: scratchpad['inventory'].append("Blue Key")
    if "Steve" in new_log: scratchpad['npcs'].append("Steve")
    if "password" in new_log: scratchpad['knowledge'].append("Password: Shadow")
    return scratchpad

def run_context_engineering_benchmark():
    print("--- Starting Experiment 4: Context Strategies ---")
    
    history_log = []
    scratchpad = {'inventory': [], 'npcs': [], 'knowledge': []}
    
    # 1. Execute 10 Steps
    for i in range(NUM_ACTIONS):
        output = generate_action_output(i)
        history_log.append(output)
        scratchpad = strategy_write(scratchpad, output)
    
    print(f"Simulation Complete. Total History Length: {len(history_log)} items.")
    
    # 2. Test Query: "What color was the key?" (Info from Step 1)
    query = "Key color"
    print(f"\nQuerying: '{query}' (Target: Blue)")
    
    # --- Evaluate SELECT ---
    context_select = strategy_select(history_log, query)
    print(f"\n[SELECT Strategy Context]:\n{context_select}")
    acc_select = "PASS" if "Blue" in context_select else "FAIL"
    
    # --- Evaluate COMPRESS ---
    context_compress = strategy_compress(history_log)
    print(f"\n[COMPRESS Strategy Context]:\n{context_compress}")
    # Note: Compression might lose the specific adjective "Blue" if over-summarized
    acc_compress = "PASS" if "Blue" in context_compress else "FAIL (Lossy)" 
    
    # --- Evaluate WRITE ---
    context_write = str(scratchpad)
    print(f"\n[WRITE Strategy Context]:\n{context_write}")
    acc_write = "PASS" if "Blue" in context_write else "FAIL"

    # 3. Final Report
    print("\n--- Results Summary ---")
    print(f"SELECT:   {acc_select}")
    print(f"COMPRESS: {acc_compress}")
    print(f"WRITE:    {acc_write}")

run_context_engineering_benchmark()