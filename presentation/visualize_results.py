"""
Visualization Script for LLM Experiments.

Usage:
    python3 visualize_results.py

Requirements:
    pip install matplotlib numpy
"""

import json
import glob
import os
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

def load_latest_result(task_dir):
    """Finds and loads the most recent JSON result file for a task."""
    pattern = os.path.join(task_dir, "results", "*.json")
    files = glob.glob(pattern)
    if not files:
        print(f"Warning: No results found in {task_dir}")
        return None
    latest_file = max(files, key=os.path.getctime)
    print(f"Loading {latest_file}...")
    with open(latest_file, 'r') as f:
        return json.load(f)

def plot_task1(data):
    if not data: return
    print("Plotting Task 1...")
    
    stats = data.get('position_statistics', {})
    positions = ['start', 'middle', 'end']
    accuracies = []
    
    for pos in positions:
        if pos in stats:
            accuracies.append(stats[pos]['accuracy_pct'])
        else:
            accuracies.append(0)
            
    plt.figure(figsize=(8, 5))
    plt.bar(positions, accuracies, color=['green', 'orange', 'green'])
    plt.title('Task 1: Lost in the Middle - Retrieval Accuracy')
    plt.ylabel('Accuracy (%)')
    plt.ylim(0, 110)
    plt.grid(axis='y', alpha=0.3)
    plt.savefig('presentation/task1_accuracy.png')
    plt.close()

def plot_task2(data):
    if not data: return
    print("Plotting Task 2...")
    
    # Data is a list of dicts in the file, but sometimes wrapped.
    # Based on my run, it's a list.
    if isinstance(data, list):
        results = data
    else:
        # If wrapped? The logic in run_experiment saves a list `results`.
        results = data 
        
    doc_counts = [r['doc_count'] for r in results]
    latencies = [r['latency'] for r in results]
    accuracies = [r['accuracy'] * 100 for r in results]
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Latency (Line)
    color = 'tab:red'
    ax1.set_xlabel('Context Size (Documents)')
    ax1.set_ylabel('Latency (s)', color=color)
    ax1.plot(doc_counts, latencies, color=color, marker='o', label='Latency')
    ax1.tick_params(axis='y', labelcolor=color)
    
    # Accuracy (Bar)
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Accuracy (%)', color=color)
    ax2.bar(doc_counts, accuracies, color=color, alpha=0.3, width=2, label='Accuracy')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim(0, 110)
    
    plt.title('Task 2: Context Size Impact (Latency vs Accuracy)')
    fig.tight_layout()
    plt.savefig('presentation/task2_impact.png')
    plt.close()

def plot_task3(data):
    if not data: return
    print("Plotting Task 3...")
    
    stats_a = data.get('stats_a', {})
    stats_b = data.get('stats_b', {})
    
    modes = ['Full Context', 'RAG']
    latencies = [stats_a.get('avg_latency', 0), stats_b.get('avg_latency', 0)]
    accuracies = [stats_a.get('accuracy', 0), stats_b.get('accuracy', 0)]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Latency
    ax1.bar(modes, latencies, color=['salmon', 'skyblue'])
    ax1.set_title('Average Latency (Lower is Better)')
    ax1.set_ylabel('Seconds')
    
    # Accuracy
    ax2.bar(modes, accuracies, color=['salmon', 'skyblue'])
    ax2.set_title('Accuracy (Higher is Better)')
    ax2.set_ylabel('Percentage (%)')
    ax2.set_ylim(0, 110)
    
    plt.suptitle('Task 3: RAG vs Full Context Performance')
    plt.savefig('presentation/task3_comparison.png')
    plt.close()

def main():
    if not os.path.exists('presentation'):
        os.makedirs('presentation')
        
    # Task 1
    t1_data = load_latest_result("task1_experiment")
    if t1_data: plot_task1(t1_data)
    
    # Task 2
    t2_data = load_latest_result("task2_experiment")
    if t2_data: plot_task2(t2_data)
    
    # Task 3
    t3_data = load_latest_result("task3_experiment")
    if t3_data: plot_task3(t3_data)
    
    print("\nVisualization complete. Check 'presentation/' folder for PNGs.")

if __name__ == "__main__":
    try:
        main()
    except ImportError:
        print("Error: matplotlib or numpy not installed.")
        print("Please run: pip install matplotlib numpy")
