"""Common utilities for all experiments."""

import sys
import yaml
import random
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict

# --- Logging ---

def setup_logger(
    name: str,
    log_dir: Optional[Path] = None,
    level: str = "INFO",
    console: bool = True,
    file: bool = True
) -> logging.Logger:
    """Configure and return a logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(level.upper())
    logger.handlers = []  # Clear existing handlers

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if file and log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / f"{name.lower().replace(' ', '_')}.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# --- Reproducibility ---

def set_seed(seed: int = 42):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    # np.random.seed(seed) # Removed numpy
    # torch.manual_seed(seed) # If torch is added later

# --- Configuration Base ---

def load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """Load raw YAML config."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def save_yaml_config(config_data: Dict[str, Any], output_path: Path):
    """Save config to YAML."""
    with open(output_path, 'w') as f:
        yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)

# --- I/O & Reporting ---

def save_json_results(results: Dict[str, Any], output_dir: Path, filename_prefix: str = "results"):
    """Save results to JSON with timestamp."""
    output_dir.mkdir(parents=True, exist_ok=True)
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.json"
    
    # Handle non-serializable objects
    def default_serializer(obj):
        # Removed numpy checks
        return str(obj)

    with open(output_dir / filename, 'w') as f:
        json.dump(results, f, indent=2, default=default_serializer)
    
    return output_dir / filename

