import json
import glob
import os
from pathlib import Path
from typing import Dict, Any, List

# --- Utility Functions ---

def load_latest_result(task_dir: str) -> Dict[str, Any]:
    """Load the most recent results.json file from the given directory."""
    search_path = os.path.join(task_dir, "results", "results_*.json")
    files = glob.glob(search_path)
    if not files:
        # Fallback to standard results.json if timestamped one missing
        fallback = os.path.join(task_dir, "results", "results.json")
        if os.path.exists(fallback):
            with open(fallback, 'r') as f:
                return json.load(f)
        return {}
    
    # Sort by modification time (or filename timestamp)
    latest_file = max(files, key=os.path.getctime)
    with open(latest_file, 'r') as f:
        return json.load(f)

def draw_bar(value: float, max_value: float, width: int = 20) -> str:
    """Draw a unicode progress bar."""
    if max_value == 0:
        return "░" * width
    ratio = value / max_value
    filled = int(ratio * width)
    empty = width - filled
    return "█" * filled + "░" * empty

def format_header(title: str) -> str:
    border = "═" * 60
    return f"╔{border}╗\n║ {title.center(58)} ║\n╚{border}╝"

# --- Task Reports ---

def report_task1(data: Dict[str, Any]) -> str:
    if not data: return "No data found for Task 1."
    
    stats = data.get('statistics', {})
    
    # Extract data
    positions = ['start', 'middle', 'end']
    accuracies = []
    counts = []
    
    output = []
    output.append(format_header("TASK 1: LOST IN THE MIDDLE (Positional Bias)"))
    output.append("\nHypothesis: Facts at edges are retrieved better than in the middle.\n")
    
    # Table Header
    output.append(f"{'Position':<15} | {'Accuracy':<10} | {'Count':<8} | {'Visual':<22}")
    output.append("━" * 60)
    
    for pos in positions:
        s = stats.get(pos, {'accuracy': 0, 'count': 0})
        acc = s['accuracy'] * 100
        count = s['count']
        accuracies.append(acc)
        
        bar = draw_bar(acc, 100, 20)
        status = "✓" if acc > 80 else ("~" if acc > 40 else "✗")
        
        output.append(f"{pos.upper():<15} | {acc:>5.1f}%     | {count:<8} | {bar} {status}")
        
    output.append("\nAnalysis:")
    edge_avg = (stats.get('start', {}).get('accuracy', 0) + stats.get('end', {}).get('accuracy', 0)) / 2 * 100
    mid_avg = stats.get('middle', {}).get('accuracy', 0) * 100
    
    output.append(f"• Edge Accuracy (Start/End): {edge_avg:.1f}%")
    output.append(f"• Middle Accuracy:           {mid_avg:.1f}%")
    
    if edge_avg > mid_avg:
        output.append("\n✅ CONCLUSION: Hypothesis CONFIRMED. Performance drops in the middle.")
    else:
        output.append("\n❌ CONCLUSION: Hypothesis NOT confirmed (or limited by model capability).")
        
    return "\n".join(output)

def report_task2(data: Dict[str, Any]) -> str:
    if not data: return "No data found for Task 2."
    
    # Data is a list of dicts in the root or under a key?
    # Based on task2 code: save_json_results(results, ...) -> results is a list.
    # But save_json_results might wrap it? No, common/utils.py dumps object directly.
    # Let's check if it's a list or dict.
    results = data if isinstance(data, list) else data.get('results', [])
    
    output = []
    output.append(format_header("TASK 2: CONTEXT WINDOW SIZE IMPACT"))
    output.append("\nHypothesis: Latency increases linearly; Accuracy degrades with size.\n")
    
    output.append(f"{'Docs':<6} | {'Tokens':<8} | {'Latency (s)':<12} | {'Accuracy':<10} | {'Latency Visual':<15}")
    output.append("━" * 65)
    
    max_latency = max((r['latency'] for r in results), default=1.0)
    
    for r in results:
        doc = r['doc_count']
        tokens = r['estimated_tokens']
        lat = r['latency']
        acc = r['accuracy'] * 100
        
        bar = draw_bar(lat, max_latency, 15)
        
        output.append(f"{doc:<6} | {tokens:<8} | {lat:<12.4f} | {acc:>5.1f}%     | {bar}")
        
    output.append("\nAnalysis:")
    # Check linearity roughly
    latencies = [r['latency'] for r in results]
    if len(latencies) > 1 and latencies[-1] > latencies[0]:
        output.append("✅ Latency increases with context size (Validated).")
    
    # Check accuracy drop
    accuracies = [r['accuracy'] for r in results]
    if any(a < 1.0 for a in accuracies):
        output.append("✅ Accuracy degradation observed (Validated).")
    else:
        output.append("ℹ️ No accuracy degradation observed (Model handled context well).")
        
    return "\n".join(output)

def report_task3(data: Dict[str, Any]) -> str:
    if not data: return "No data found for Task 3."
    
    stats_a = data.get('stats_a', {})
    stats_b = data.get('stats_b', {})
    
    output = []
    output.append(format_header("TASK 3: RAG vs FULL CONTEXT"))
    output.append("\nHypothesis: RAG is faster and more accurate than Full Context.\n")
    
    # Comparison Table
    output.append(f"{'Metric':<20} | {'Mode A (Full)':<15} | {'Mode B (RAG)':<15} | {'Improvement':<15}")
    output.append("━" * 70)
    
    lat_a = stats_a.get('avg_latency', 0)
    lat_b = stats_b.get('avg_latency', 0)
    acc_a = stats_a.get('accuracy', 0)
    acc_b = stats_b.get('accuracy', 0)
    
    lat_imp = ((lat_a - lat_b) / lat_a * 100) if lat_a > 0 else 0
    acc_imp = (acc_b - acc_a)
    
    output.append(f"{'Avg Latency':<20} | {lat_a:<15.4f} | {lat_b:<15.4f} | {lat_imp:+.1f}% (Faster)")
    output.append(f"{'Accuracy':<20} | {acc_a:<15.1f}% | {acc_b:<15.1f}% | {acc_imp:+.1f}% (Points)")
    
    # Visual Comparison
    output.append("\nVisual Comparison:")
    output.append(f"Latency A: {draw_bar(lat_a, max(lat_a, lat_b), 30)} {lat_a:.2f}s")
    output.append(f"Latency B: {draw_bar(lat_b, max(lat_a, lat_b), 30)} {lat_b:.2f}s")
    output.append("")
    output.append(f"Accuracy A: {draw_bar(acc_a, 100, 30)} {acc_a:.1f}%")
    output.append(f"Accuracy B: {draw_bar(acc_b, 100, 30)} {acc_b:.1f}%")
    
    output.append("\nAnalysis:")
    if lat_b < lat_a and acc_b >= acc_a:
        output.append("✅ CONCLUSION: RAG outperforms Full Context in both Latency and Accuracy.")
    else:
         output.append("ℹ️ CONCLUSION: Results mixed.")
         
    return "\n".join(output)

def report_task4(data: Dict[str, Any]) -> str:
    if not data: return "No data found for Task 4."
    
    # data keys: select, compress, write
    
    output = []
    output.append(format_header("TASK 4: CONTEXT STRATEGIES"))
    output.append("\nHypothesis: Structured/Selected memory > Compression.\n")
    
    output.append(f"{'Strategy':<15} | {'Result':<10} | {'Details'}")
    output.append("━" * 50)
    
    strategies = ['select', 'compress', 'write']
    for strat in strategies:
        res = data.get(strat, {})
        passed = res.get('pass', False)
        status = "✅ PASS" if passed else "❌ FAIL"
        
        # Extract snippet of context
        ctx = res.get('context', '').replace('\n', ' ')[:40] + "..."
        
        output.append(f"{strat.upper():<15} | {status:<10} | {ctx}")
        
    output.append("\nAnalysis:")
    if data.get('select', {}).get('pass') and data.get('write', {}).get('pass') and not data.get('compress', {}).get('pass'):
        output.append("✅ CONCLUSION: Hypothesis Confirmed. Compression lost detail.")
    else:
        output.append("ℹ️ CONCLUSION: Results vary from hypothesis.")

    return "\n".join(output)

def main():
    root = Path(__file__).parent.parent
    
    # Load Data
    data1 = load_latest_result(str(root / "task1_experiment"))
    data2 = load_latest_result(str(root / "task2_experiment"))
    data3 = load_latest_result(str(root / "task3_experiment"))
    data4 = load_latest_result(str(root / "task4_experiment"))
    
    # Generate Reports
    rep1 = report_task1(data1)
    rep2 = report_task2(data2)
    rep3 = report_task3(data3)
    rep4 = report_task4(data4)
    
    # Write individual files
    with open(root / "presentation" / "task1_results.txt", "w") as f: f.write(rep1)
    with open(root / "presentation" / "task2_results.txt", "w") as f: f.write(rep2)
    with open(root / "presentation" / "task3_results.txt", "w") as f: f.write(rep3)
    with open(root / "presentation" / "task4_results.txt", "w") as f: f.write(rep4)
    
    # Write Consolidated README
    with open(root / "presentation" / "README.md", "w") as f:
        f.write("# LLM Experiments: Final Results Report\n\n")
        f.write("Generated from actual experiment data.\n\n")
        
        f.write("```\n")
        f.write(rep1)
        f.write("\n```\n\n")
        
        f.write("```\n")
        f.write(rep2)
        f.write("\n```\n\n")
        
        f.write("```\n")
        f.write(rep3)
        f.write("\n```\n\n")
        
        f.write("```\n")
        f.write(rep4)
        f.write("\n```\n")
        
    print("Reports generated in presentation/ folder.")

if __name__ == "__main__":
    main()
