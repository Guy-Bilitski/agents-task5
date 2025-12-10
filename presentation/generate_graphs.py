import json
import glob
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

# Setup style
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = [10, 6]
plt.rcParams['font.size'] = 12

def load_latest_result(task_dir: str) -> Dict[str, Any]:
    """Load the most recent results.json file."""
    search_path = os.path.join(task_dir, "results", "results_*.json")
    files = glob.glob(search_path)
    if not files:
        fallback = os.path.join(task_dir, "results", "results.json")
        if os.path.exists(fallback):
            with open(fallback, 'r') as f: return json.load(f)
        return {}
    latest_file = max(files, key=os.path.getctime)
    with open(latest_file, 'r') as f: return json.load(f)

def generate_task1_graph(data: Dict[str, Any], output_path: str):
    if not data: return
    
    stats = data.get('statistics', {})
    positions = ['Start (0%)', 'Middle (50%)', 'End (100%)']
    keys = ['start', 'middle', 'end']
    accuracies = [stats.get(k, {'accuracy': 0}).get('accuracy', 0) * 100 for k in keys]
    
    plt.figure()
    bars = plt.bar(positions, accuracies, color=['#4CAF50', '#F44336', '#FF9800'])
    plt.title('Task 1: Lost in the Middle - Retrieval Accuracy')
    plt.ylabel('Accuracy (%)')
    plt.ylim(0, 105)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom')
                
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Saved {output_path}")

def generate_task2_graph(data: Dict[str, Any], output_path: str):
    if not data: return
    
    # Check if results is a list or dict
    results = data if isinstance(data, list) else data.get('results', [])
    if not results: return
    
    df = pd.DataFrame(results)
    
    fig, ax1 = plt.subplots()
    
    # Plot Latency (Line)
    color = 'tab:blue'
    ax1.set_xlabel('Number of Documents')
    ax1.set_ylabel('Latency (s)', color=color)
    ax1.plot(df['doc_count'], df['latency'], color=color, marker='o', linewidth=2, label='Latency')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, alpha=0.3)
    
    # Plot Accuracy (Bar/Scatter) - Right Axis
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Accuracy', color=color)
    # Convert accuracy to percentage if it's 0-1
    acc_vals = df['accuracy'] * 100 if df['accuracy'].max() <= 1.0 else df['accuracy']
    
    ax2.bar(df['doc_count'], acc_vals, width=2, alpha=0.3, color=color, label='Accuracy')
    ax2.set_ylim(0, 105)
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title('Task 2: Context Window Size Impact\nLatency vs Accuracy')
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Saved {output_path}")

def generate_task3_graph(data: Dict[str, Any], output_path: str):
    if not data: return
    
    stats_a = data.get('stats_a', {})
    stats_b = data.get('stats_b', {})
    
    # Metrics
    metrics = ['Latency (s)', 'Accuracy (%)']
    full_context = [stats_a.get('avg_latency', 0), stats_a.get('accuracy', 0)]
    rag = [stats_b.get('avg_latency', 0), stats_b.get('accuracy', 0)]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, full_context, width, label='Full Context', color='#9E9E9E')
    rects2 = ax.bar(x + width/2, rag, width, label='RAG', color='#2196F3')
    
    ax.set_ylabel('Score')
    ax.set_title('Task 3: RAG vs Full Context Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    
    # Label bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Saved {output_path}")

def generate_task4_graph(data: Dict[str, Any], output_path: str):
    if not data: return
    
    strategies = ['SELECT', 'COMPRESS', 'WRITE']
    keys = ['select', 'compress', 'write']
    
    # Convert pass/fail to 1/0
    scores = []
    colors = []
    
    for k in keys:
        passed = data.get(k, {}).get('pass', False)
        scores.append(1 if passed else 0)
        colors.append('#4CAF50' if passed else '#F44336')
        
    plt.figure()
    bars = plt.bar(strategies, scores, color=colors)
    plt.title('Task 4: Context Management Strategy Success')
    plt.ylabel('Outcome (1=Pass, 0=Fail)')
    plt.yticks([0, 1], ['FAIL', 'PASS'])
    plt.ylim(0, 1.2)
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Saved {output_path}")

def main():
    root = Path(__file__).parent.parent
    
    # Load Data
    data1 = load_latest_result(str(root / "task1_experiment"))
    data2 = load_latest_result(str(root / "task2_experiment"))
    data3 = load_latest_result(str(root / "task3_experiment"))
    data4 = load_latest_result(str(root / "task4_experiment"))
    
    # Generate Graphs
    out_dir = root / "presentation" / "images"
    
    generate_task1_graph(data1, str(out_dir / "task1_graph.png")),
    generate_task2_graph(data2, str(out_dir / "task2_graph.png")),
    generate_task3_graph(data3, str(out_dir / "task3_graph.png")),
    generate_task4_graph(data4, str(out_dir / "task4_graph.png")),

if __name__ == "__main__":
    main()
