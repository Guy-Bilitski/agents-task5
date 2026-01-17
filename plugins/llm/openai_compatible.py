"""
OpenAI-Compatible LLM Plugin.

This plugin provides support for any OpenAI-compatible API endpoint,
including:
- OpenAI GPT models
- Azure OpenAI
- Local servers (vLLM, text-generation-inference)
- Other compatible providers

Usage:
    from common.plugins import llm_registry

    # Register and use
    llm = llm_registry.create_instance(
        "openai_compatible",
        api_key="your-key",
        base_url="https://api.openai.com/v1"
    )
    result = llm.query("Context here", "What is the answer?")
"""

import os
import time
from typing import Any, Dict, Optional

import requests

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common.llm import BaseLLM
from common.plugins import plugin


@plugin(name="openai_compatible", metadata={
    "description": "OpenAI-compatible API backend",
    "version": "1.0.0",
    "author": "Project Team"
})
class OpenAICompatibleLLM(BaseLLM):
    """
    LLM backend for OpenAI-compatible API endpoints.

    Supports any API that implements the OpenAI chat completions format,
    including OpenAI, Azure OpenAI, and local inference servers.
    """

    PLUGIN_NAME = "openai_compatible"

    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
        temperature: float = 0.0,
        max_tokens: int = 100,
        timeout: int = 60
    ):
        """
        Initialize the OpenAI-compatible LLM.

        Args:
            model_name: Model identifier
            api_key: API key (or set OPENAI_API_KEY env var)
            base_url: API base URL
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
        """
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    def query(self, context: str, question: str, **kwargs) -> Dict[str, Any]:
        """
        Query the OpenAI-compatible API.

        Args:
            context: Input context
            question: User question
            **kwargs: Additional arguments (expected_answer for accuracy check)

        Returns:
            Dict with response, latency, token_count, is_accurate
        """
        start_time = time.time()

        # Construct messages
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Answer questions based on the provided context."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}\n\nAnswer briefly:"}
        ]

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                },
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            llm_response = result["choices"][0]["message"]["content"].strip()

            # Calculate metrics
            latency = time.time() - start_time
            token_count = result.get("usage", {}).get("total_tokens", len(context.split()))

            # Check accuracy
            expected = kwargs.get("expected_answer", "")
            is_accurate = expected.lower() in llm_response.lower() if expected else False

            return {
                "response": llm_response,
                "latency": latency,
                "token_count": token_count,
                "is_accurate": is_accurate
            }

        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "latency": time.time() - start_time,
                "token_count": len(context.split()),
                "is_accurate": False
            }

    def health_check(self) -> bool:
        """Check if the API is accessible."""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
