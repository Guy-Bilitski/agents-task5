"""Helper utilities for experiment."""

import random
import logging
from datetime import datetime
from pathlib import Path


def setup_logging(log_file="experiment.log"):
    """Setup basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def set_seed(seed):
    """Set random seed for reproducibility."""
    random.seed(seed)


def generate_filler_text(num_words):
    """Generate filler text."""
    sentences = [
        "The weather today was quite pleasant with clear skies overhead.",
        "Historical records indicate that ancient civilizations thrived in this region.",
        "Technology has transformed the way people communicate across vast distances.",
        "Medical advancements have improved healthcare outcomes for countless patients.",
        "Cultural traditions have been passed down through generations of families.",
    ]
    
    text = []
    while len(" ".join(text).split()) < num_words:
        text.append(random.choice(sentences))
    
    return " ".join(" ".join(text).split()[:num_words])


def generate_document(position_pct, doc_length, fact):
    """Generate document with fact at specified position."""
    filler = generate_filler_text(doc_length)
    words = filler.split()
    
    insert_idx = int(len(words) * position_pct)
    doc_text = " ".join(words[:insert_idx] + fact.split() + words[insert_idx:])
    
    return {
        'text': doc_text,
        'position_pct': position_pct * 100,
        'word_count': len(doc_text.split())
    }


def save_results(results, output_dir="results"):
    """Save results to JSON."""
    import json
    
    Path(output_dir).mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(output_dir) / f"results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    return output_file
