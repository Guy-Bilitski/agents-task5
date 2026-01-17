"""
Pytest Configuration and Shared Fixtures.

This module provides test fixtures, configuration, and utilities
shared across all test modules.
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from common.llm import BaseLLM, MockLLM, OllamaLLM
from common.utils import setup_logger, set_seed, load_yaml_config
from common.data import generate_text_block, insert_needle, TEMPLATES


# =============================================================================
# Configuration Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def test_data_dir(project_root: Path) -> Path:
    """Return the test data directory."""
    data_dir = project_root / "tests" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Return a sample experiment configuration."""
    return {
        "experiment": {
            "name": "test_experiment",
            "seed": 42,
            "num_trials": 3,
        },
        "llm": {
            "model_name": "llama3.2:1b",
            "temperature": 0.0,
            "max_tokens": 100,
        },
        "data": {
            "domain": "generic",
            "min_words": 100,
        }
    }


@pytest.fixture
def sample_yaml_config(temp_dir: Path, sample_config: Dict[str, Any]) -> Path:
    """Create a sample YAML config file and return its path."""
    import yaml
    config_path = temp_dir / "test_config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(sample_config, f)
    return config_path


# =============================================================================
# LLM Fixtures
# =============================================================================

@pytest.fixture
def mock_llm() -> MockLLM:
    """Create a configured MockLLM instance for testing."""
    return MockLLM(
        latency_base=0.01,  # Fast for testing
        latency_per_token=0.0001,
        noise_threshold=5000,
        noise_prob_low=0.0,
        noise_prob_high=0.5
    )


@pytest.fixture
def mock_llm_deterministic() -> MockLLM:
    """Create a deterministic MockLLM for predictable tests."""
    set_seed(42)
    return MockLLM(
        latency_base=0.01,
        latency_per_token=0.0001,
        noise_threshold=10000,  # High threshold = always accurate
        noise_prob_low=0.0,
        noise_prob_high=0.0  # Never fail
    )


@pytest.fixture
def mock_ollama_response() -> Dict[str, Any]:
    """Return a mock Ollama API response."""
    return {
        "model": "llama3.2:1b",
        "created_at": "2026-01-17T10:00:00Z",
        "response": "The answer is 42.",
        "done": True,
        "context": [1, 2, 3],
        "total_duration": 1000000000,
        "load_duration": 100000000,
        "prompt_eval_count": 50,
        "prompt_eval_duration": 500000000,
        "eval_count": 10,
        "eval_duration": 400000000
    }


@pytest.fixture
def patched_ollama_llm(mock_ollama_response: Dict[str, Any]) -> OllamaLLM:
    """Create an OllamaLLM with mocked HTTP requests."""
    with patch('common.llm.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_ollama_response
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        yield OllamaLLM()


# =============================================================================
# Data Fixtures
# =============================================================================

@pytest.fixture
def sample_documents() -> list[str]:
    """Return sample documents for testing."""
    return [
        "This is the first document about technology and innovation.",
        "The second document discusses history and culture.",
        "A third document covers science and mathematics.",
        "The fourth document explores art and creativity.",
        "Finally, the fifth document examines economics and markets."
    ]


@pytest.fixture
def sample_needle() -> str:
    """Return a sample needle fact for testing."""
    return "The secret code is ALPHA123."


@pytest.fixture
def sample_haystack(sample_documents: list[str], sample_needle: str) -> str:
    """Create a sample haystack with a needle inserted."""
    text = " ".join(sample_documents)
    return insert_needle(text, sample_needle, position="middle")


@pytest.fixture
def large_context() -> str:
    """Generate a large context for stress testing."""
    set_seed(42)
    blocks = [generate_text_block("generic", min_words=500) for _ in range(10)]
    return " ".join(blocks)


# =============================================================================
# Result Fixtures
# =============================================================================

@pytest.fixture
def sample_experiment_results() -> Dict[str, Any]:
    """Return sample experiment results for testing."""
    return {
        "experiment_name": "test_experiment",
        "timestamp": "2026-01-17T10:00:00",
        "config": {
            "seed": 42,
            "num_trials": 3
        },
        "trials": [
            {
                "trial_id": 1,
                "accuracy": 1.0,
                "latency": 0.5,
                "tokens": 100
            },
            {
                "trial_id": 2,
                "accuracy": 1.0,
                "latency": 0.6,
                "tokens": 100
            },
            {
                "trial_id": 3,
                "accuracy": 0.0,
                "latency": 0.7,
                "tokens": 100
            }
        ],
        "summary": {
            "accuracy_mean": 0.667,
            "accuracy_std": 0.471,
            "latency_mean": 0.6,
            "latency_std": 0.082
        }
    }


# =============================================================================
# Helper Functions
# =============================================================================

def assert_valid_llm_response(response: Dict[str, Any]) -> None:
    """Assert that an LLM response has the expected structure."""
    assert isinstance(response, dict)
    assert "response" in response
    assert "latency" in response
    assert "token_count" in response
    assert "is_accurate" in response
    assert isinstance(response["latency"], (int, float))
    assert response["latency"] >= 0
    assert isinstance(response["token_count"], int)
    assert response["token_count"] >= 0


def assert_valid_experiment_results(results: Dict[str, Any]) -> None:
    """Assert that experiment results have the expected structure."""
    assert isinstance(results, dict)
    assert "experiment_name" in results or "experiment" in results
    assert "trials" in results or "results" in results


# =============================================================================
# Markers
# =============================================================================

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "llm: mark test as requiring an LLM backend"
    )


# =============================================================================
# Session Setup
# =============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment before running tests."""
    # Set seed for reproducibility
    set_seed(42)

    # Set environment variables for testing
    os.environ["TESTING"] = "true"

    yield

    # Cleanup
    if "TESTING" in os.environ:
        del os.environ["TESTING"]
