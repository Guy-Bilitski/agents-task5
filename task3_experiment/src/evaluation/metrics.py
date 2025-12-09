"""Evaluation metrics."""

from typing import List, Dict, Any

def calculate_statistics(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate average latency and accuracy.
    """
    if not results:
        return {
            "avg_latency": 0.0,
            "accuracy": 0.0,
            "count": 0
        }
        
    total_latency = sum(r['latency'] for r in results)
    total_correct = sum(1 for r in results if r['is_accurate'])
    count = len(results)
    
    return {
        "avg_latency": total_latency / count,
        "accuracy": (total_correct / count) * 100.0,
        "count": count
    }
