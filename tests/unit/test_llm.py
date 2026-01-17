"""
Unit Tests for LLM Module.

Tests for BaseLLM, MockLLM, and OllamaLLM classes.
"""

import time
from unittest.mock import MagicMock, patch

import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common.llm import BaseLLM, MockLLM, OllamaLLM
from common.utils import set_seed


class TestBaseLLM:
    """Tests for the BaseLLM abstract base class."""

    def test_cannot_instantiate_directly(self):
        """BaseLLM should not be instantiable directly."""
        with pytest.raises(TypeError):
            BaseLLM()

    def test_subclass_must_implement_query(self):
        """Subclasses must implement the query method."""

        class IncompleteLLM(BaseLLM):
            pass

        with pytest.raises(TypeError):
            IncompleteLLM()

    def test_subclass_with_query_can_instantiate(self):
        """Subclasses implementing query can be instantiated."""

        class CompleteLLM(BaseLLM):
            def query(self, context: str, question: str, **kwargs):
                return {"response": "test", "latency": 0.1, "token_count": 10, "is_accurate": True}

        llm = CompleteLLM()
        assert llm is not None


class TestMockLLM:
    """Tests for the MockLLM implementation."""

    def test_initialization_default_params(self):
        """MockLLM should initialize with default parameters."""
        llm = MockLLM()
        assert llm.latency_base == 0.5
        assert llm.latency_per_token == 0.0005
        assert llm.noise_threshold == 5000
        assert llm.noise_prob_low == 0.0
        assert llm.noise_prob_high == 0.5

    def test_initialization_custom_params(self):
        """MockLLM should accept custom parameters."""
        llm = MockLLM(
            latency_base=1.0,
            latency_per_token=0.001,
            noise_threshold=10000,
            noise_prob_low=0.1,
            noise_prob_high=0.8
        )
        assert llm.latency_base == 1.0
        assert llm.latency_per_token == 0.001
        assert llm.noise_threshold == 10000
        assert llm.noise_prob_low == 0.1
        assert llm.noise_prob_high == 0.8

    def test_query_returns_required_fields(self, mock_llm):
        """Query should return all required fields."""
        result = mock_llm.query("Some context", "What is the answer?")

        assert "response" in result
        assert "latency" in result
        assert "token_count" in result
        assert "is_accurate" in result

    def test_query_token_count_based_on_context(self, mock_llm):
        """Token count should be based on context word count."""
        short_context = "Hello world"  # 2 words
        long_context = "The quick brown fox jumps over the lazy dog"  # 9 words

        short_result = mock_llm.query(short_context, "Test?")
        long_result = mock_llm.query(long_context, "Test?")

        assert short_result["token_count"] == 2
        assert long_result["token_count"] == 9

    def test_query_latency_increases_with_tokens(self, mock_llm):
        """Latency should increase with context length."""
        short_context = "Hello world"
        long_context = " ".join(["word"] * 1000)

        short_result = mock_llm.query(short_context, "Test?")
        long_result = mock_llm.query(long_context, "Test?")

        # Long context should have higher latency (allowing for jitter)
        assert long_result["latency"] > short_result["latency"]

    def test_query_with_expected_answer_accurate(self, mock_llm_deterministic):
        """When accurate, response should contain expected answer."""
        result = mock_llm_deterministic.query(
            "Some context about a topic",
            "What is the answer?",
            expected_answer="42"
        )

        assert result["is_accurate"] is True
        assert "42" in result["response"]

    def test_query_below_noise_threshold(self):
        """Queries below noise threshold should be accurate."""
        set_seed(42)
        llm = MockLLM(noise_threshold=10000, noise_prob_low=0.0)

        # Short context (well below threshold)
        result = llm.query("Short context", "Test?", expected_answer="test")
        assert result["is_accurate"] is True

    def test_query_above_noise_threshold_may_fail(self):
        """Queries above noise threshold may be inaccurate."""
        set_seed(42)
        llm = MockLLM(noise_threshold=10, noise_prob_high=1.0)

        # Context above threshold
        long_context = " ".join(["word"] * 100)
        result = llm.query(long_context, "Test?", expected_answer="test")

        # With noise_prob_high=1.0, should always fail
        assert result["is_accurate"] is False
        assert "unsure" in result["response"].lower()

    def test_query_latency_is_positive(self, mock_llm):
        """Latency should always be positive."""
        result = mock_llm.query("Test", "Question?")
        assert result["latency"] > 0

    def test_query_response_is_string(self, mock_llm):
        """Response should be a string."""
        result = mock_llm.query("Test", "Question?")
        assert isinstance(result["response"], str)


class TestOllamaLLM:
    """Tests for the OllamaLLM implementation."""

    def test_initialization_default_params(self):
        """OllamaLLM should initialize with default parameters."""
        llm = OllamaLLM()
        assert llm.model_name == "llama3.2:1b"
        assert llm.base_url == "http://localhost:11434"
        assert llm.temperature == 0.0
        assert llm.max_tokens == 100
        assert llm.timeout == 120

    def test_initialization_custom_params(self):
        """OllamaLLM should accept custom parameters."""
        llm = OllamaLLM(
            model_name="custom-model",
            base_url="http://custom:8080",
            temperature=0.5,
            max_tokens=200,
            timeout=60
        )
        assert llm.model_name == "custom-model"
        assert llm.base_url == "http://custom:8080"
        assert llm.temperature == 0.5
        assert llm.max_tokens == 200
        assert llm.timeout == 60

    def test_query_with_mocked_request(self, mock_ollama_response):
        """Query should work with mocked HTTP request."""
        with patch('common.llm.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_ollama_response
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            llm = OllamaLLM()
            result = llm.query("Test context", "What is the answer?")

            assert "response" in result
            assert result["response"] == "The answer is 42."
            assert result["latency"] > 0
            assert result["token_count"] == 2  # "Test context" = 2 words

    def test_query_constructs_correct_prompt(self, mock_ollama_response):
        """Query should construct the prompt correctly."""
        with patch('common.llm.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_ollama_response
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            llm = OllamaLLM()
            llm.query("My context", "My question?")

            # Check the call was made with correct structure
            call_args = mock_post.call_args
            json_data = call_args[1]["json"]

            assert "prompt" in json_data
            assert "My context" in json_data["prompt"]
            assert "My question?" in json_data["prompt"]

    def test_query_accuracy_check_with_expected_answer(self, mock_ollama_response):
        """Query should check accuracy when expected_answer provided."""
        with patch('common.llm.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_ollama_response
            mock_post.return_value = mock_response

            llm = OllamaLLM()
            result = llm.query("Context", "Question?", expected_answer="42")

            # Response contains "42", so should be accurate
            assert result["is_accurate"] is True

    def test_query_accuracy_check_with_needle_fact(self, mock_ollama_response):
        """Query should check accuracy with needle_fact parameter."""
        with patch('common.llm.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_ollama_response
            mock_post.return_value = mock_response

            llm = OllamaLLM()
            result = llm.query("Context", "Question?", needle_fact="42")

            assert result["is_accurate"] is True

    def test_query_handles_http_error(self):
        """Query should handle HTTP errors gracefully."""
        with patch('common.llm.requests.post') as mock_post:
            mock_post.side_effect = Exception("Connection refused")

            llm = OllamaLLM()
            result = llm.query("Context", "Question?")

            assert "Error" in result["response"]
            assert result["is_accurate"] is False

    def test_query_handles_timeout(self):
        """Query should handle timeouts gracefully."""
        with patch('common.llm.requests.post') as mock_post:
            import requests
            mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

            llm = OllamaLLM()
            result = llm.query("Context", "Question?")

            assert "Error" in result["response"]
            assert result["is_accurate"] is False

    def test_query_uses_correct_endpoint(self, mock_ollama_response):
        """Query should call the correct Ollama endpoint."""
        with patch('common.llm.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_ollama_response
            mock_post.return_value = mock_response

            llm = OllamaLLM(base_url="http://test:1234")
            llm.query("Context", "Question?")

            call_args = mock_post.call_args
            assert call_args[0][0] == "http://test:1234/api/generate"

    def test_query_passes_model_options(self, mock_ollama_response):
        """Query should pass temperature and max_tokens to Ollama."""
        with patch('common.llm.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_ollama_response
            mock_post.return_value = mock_response

            llm = OllamaLLM(temperature=0.7, max_tokens=150)
            llm.query("Context", "Question?")

            call_args = mock_post.call_args
            json_data = call_args[1]["json"]

            assert json_data["options"]["temperature"] == 0.7
            assert json_data["options"]["num_predict"] == 150


class TestLLMIntegration:
    """Integration tests for LLM classes."""

    def test_mock_llm_reproducibility(self):
        """MockLLM should produce reproducible results with same seed."""
        set_seed(42)
        llm1 = MockLLM()
        result1 = llm1.query("Context", "Question?", expected_answer="test")

        set_seed(42)
        llm2 = MockLLM()
        result2 = llm2.query("Context", "Question?", expected_answer="test")

        assert result1["is_accurate"] == result2["is_accurate"]

    def test_llm_interface_compatibility(self, mock_llm):
        """Both MockLLM and OllamaLLM should have compatible interfaces."""
        mock_result = mock_llm.query("Context", "Question?")

        with patch('common.llm.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "response": "Test response",
                "done": True
            }
            mock_post.return_value = mock_response

            ollama = OllamaLLM()
            ollama_result = ollama.query("Context", "Question?")

        # Both should have same keys
        assert set(mock_result.keys()) == set(ollama_result.keys())
