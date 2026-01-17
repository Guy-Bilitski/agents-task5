"""
Plugins Package.

This package contains extensible plugins for the LLM Context Window
Experiments platform. Plugins are automatically discovered and registered
when the plugin system is initialized.

Plugin Categories:
    - llm/: LLM backend implementations
    - strategies/: Memory management strategies
    - metrics/: Evaluation metrics
"""

from pathlib import Path

PLUGINS_DIR = Path(__file__).parent
