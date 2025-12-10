"""Common data generation utilities."""

import random
from typing import List

# Standard filler text for various domains
TEMPLATES = {
    "generic": [
        "The weather today is quite sunny and bright.",
        "History teaches us valuable lessons about the past.",
        "Mathematics is the universal language of science.",
        "Art allows for creative expression and emotion.",
        "Technology evolves at a rapid pace every year."
    ],
    "medicine": [
        "Clinical trials are essential for drug approval.",
        "Patient care requires empathy and expertise.",
        "Modern surgery utilizes robotic assistance.",
        "Vaccines have eradicated many deadly diseases.",
        "Regular checkups monitor vital health statistics."
    ],
    "law": [
        "The defendant pleaded not guilty to the charges.",
        "Contracts must be signed by all parties involved.",
        "Intellectual property laws protect innovation.",
        "The constitution guarantees fundamental rights.",
        "Litigation can be a lengthy and costly process."
    ],
    "tech": [
        "Artificial intelligence is transforming industries.",
        "Cloud computing provides scalable infrastructure.",
        "Cybersecurity is critical for data protection.",
        "Software development follows agile methodologies.",
        "Quantum computing promises exponential speedups."
    ]
}

def generate_text_block(domain: str = "generic", min_words: int = 100) -> str:
    """Generate a coherent block of text of at least min_words."""
    templates = TEMPLATES.get(domain, TEMPLATES["generic"])
    words = []
    while len(words) < min_words:
        sent = random.choice(templates)
        words.extend(sent.split())
    
    return " ".join(words[:min_words])

def insert_needle(text: str, needle: str, position: str | float = "random") -> str:
    """Insert a needle (fact) into text at a rough position."""
    words = text.split()
    total = len(words)
    
    if isinstance(position, float):
        idx = int(total * position)
        idx = max(0, min(idx, total)) # Clamp to bounds
    elif position == "start":
        idx = int(total * 0.1)
    elif position == "end":
        idx = int(total * 0.9)
    elif position == "middle":
        idx = int(total * 0.5)
    else:
        idx = random.randint(0, total)
        
    words.insert(idx, needle)
    return " ".join(words)
