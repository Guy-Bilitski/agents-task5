"""Configuration management for Task 3."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    name: str
    description: str
    version: str
    seed: int

@dataclass
class NeedleConfig:
    query: str
    fact: str
    doc_index: int

@dataclass
class DatasetConfig:
    total_docs: int
    doc_length_words: int
    target_domain: str
    distractor_domains: List[str]
    needle: NeedleConfig

@dataclass
class RAGConfig:
    chunk_size: int
    chunk_overlap: int
    top_k: int
    embedding_type: str

@dataclass
class ModelConfig:
    url: str
    name: str
    temperature: float
    max_tokens: int
    timeout: int

@dataclass
class LoggingConfig:
    level: str
    console: bool
    file: bool
    log_dir: str

@dataclass
class OutputConfig:
    results_dir: str
    save_details: bool

@dataclass
class Config:
    experiment: ExperimentConfig
    dataset: DatasetConfig
    rag: RAGConfig
    model: ModelConfig
    logging: LoggingConfig
    output: OutputConfig

def load_config(config_path: Optional[Path] = None) -> Config:
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config" / "experiment.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    return Config(
        experiment=ExperimentConfig(**config_dict['experiment']),
        dataset=DatasetConfig(
            needle=NeedleConfig(**config_dict['dataset']['needle']),
            **{k: v for k, v in config_dict['dataset'].items() if k != 'needle'}
        ),
        rag=RAGConfig(**config_dict['rag']),
        model=ModelConfig(**config_dict['model']),
        logging=LoggingConfig(**config_dict['logging']),
        output=OutputConfig(**config_dict['output'])
    )
