"""
Unit Tests for Utils Module.

Tests for utility functions including logging, configuration, and I/O.
"""

import json
import logging
import random
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common.utils import (
    setup_logger,
    set_seed,
    load_yaml_config,
    save_yaml_config,
    save_json_results,
)


class TestSetupLogger:
    """Tests for the setup_logger function."""

    def test_returns_logger_instance(self, temp_dir):
        """setup_logger should return a Logger instance."""
        logger = setup_logger("test_logger", log_dir=temp_dir)
        assert isinstance(logger, logging.Logger)

    def test_logger_has_correct_name(self, temp_dir):
        """Logger should have the specified name."""
        logger = setup_logger("my_test_logger", log_dir=temp_dir)
        assert logger.name == "my_test_logger"

    def test_logger_level_default_info(self, temp_dir):
        """Default log level should be INFO."""
        logger = setup_logger("test_logger", log_dir=temp_dir)
        assert logger.level == logging.INFO

    def test_logger_level_custom(self, temp_dir):
        """Logger should accept custom log level."""
        logger = setup_logger("test_logger", log_dir=temp_dir, level="DEBUG")
        assert logger.level == logging.DEBUG

    def test_logger_creates_file(self, temp_dir):
        """Logger should create log file when file=True."""
        logger = setup_logger("test_logger", log_dir=temp_dir, file=True)
        logger.info("Test message")

        log_files = list(temp_dir.glob("*.log"))
        assert len(log_files) == 1

    def test_logger_file_disabled(self, temp_dir):
        """Logger should not create file when file=False."""
        logger = setup_logger("test_logger", log_dir=temp_dir, file=False)
        logger.info("Test message")

        log_files = list(temp_dir.glob("*.log"))
        assert len(log_files) == 0

    def test_logger_writes_to_file(self, temp_dir):
        """Logger should write messages to file."""
        logger = setup_logger("test_logger", log_dir=temp_dir, file=True, console=False)
        test_message = "This is a test log message"
        logger.info(test_message)

        log_file = list(temp_dir.glob("*.log"))[0]
        content = log_file.read_text()
        assert test_message in content

    def test_logger_handles_spaces_in_name(self, temp_dir):
        """Logger should handle spaces in name for filename."""
        logger = setup_logger("test logger name", log_dir=temp_dir, file=True)
        logger.info("Test")

        log_files = list(temp_dir.glob("*.log"))
        assert len(log_files) == 1
        assert "test_logger_name" in log_files[0].name

    def test_logger_creates_directory(self, temp_dir):
        """Logger should create log directory if it doesn't exist."""
        nested_dir = temp_dir / "nested" / "log" / "dir"
        logger = setup_logger("test_logger", log_dir=nested_dir, file=True)
        logger.info("Test")

        assert nested_dir.exists()


class TestSetSeed:
    """Tests for the set_seed function."""

    def test_set_seed_affects_random(self):
        """set_seed should make random operations reproducible."""
        set_seed(42)
        values1 = [random.random() for _ in range(5)]

        set_seed(42)
        values2 = [random.random() for _ in range(5)]

        assert values1 == values2

    def test_different_seeds_different_values(self):
        """Different seeds should produce different random values."""
        set_seed(42)
        values1 = [random.random() for _ in range(5)]

        set_seed(123)
        values2 = [random.random() for _ in range(5)]

        assert values1 != values2

    def test_set_seed_default_value(self):
        """Default seed should be 42."""
        set_seed()  # Uses default
        values1 = [random.random() for _ in range(3)]

        set_seed(42)
        values2 = [random.random() for _ in range(3)]

        assert values1 == values2


class TestLoadYamlConfig:
    """Tests for the load_yaml_config function."""

    def test_loads_valid_yaml(self, temp_dir):
        """Should load valid YAML configuration."""
        config = {"key": "value", "number": 42}
        config_path = temp_dir / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        loaded = load_yaml_config(config_path)
        assert loaded == config

    def test_loads_nested_yaml(self, temp_dir):
        """Should load nested YAML configuration."""
        config = {
            "level1": {
                "level2": {
                    "value": "nested"
                }
            },
            "list": [1, 2, 3]
        }
        config_path = temp_dir / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        loaded = load_yaml_config(config_path)
        assert loaded["level1"]["level2"]["value"] == "nested"
        assert loaded["list"] == [1, 2, 3]

    def test_raises_on_missing_file(self, temp_dir):
        """Should raise FileNotFoundError for missing file."""
        missing_path = temp_dir / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError):
            load_yaml_config(missing_path)

    def test_loads_empty_yaml(self, temp_dir):
        """Should handle empty YAML file."""
        config_path = temp_dir / "empty.yaml"
        config_path.write_text("")

        loaded = load_yaml_config(config_path)
        assert loaded is None

    def test_accepts_path_object(self, temp_dir):
        """Should accept Path object as input."""
        config = {"test": True}
        config_path = temp_dir / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        loaded = load_yaml_config(Path(config_path))
        assert loaded == config


class TestSaveYamlConfig:
    """Tests for the save_yaml_config function."""

    def test_saves_valid_config(self, temp_dir):
        """Should save configuration to YAML file."""
        config = {"key": "value", "number": 42}
        output_path = temp_dir / "output.yaml"

        save_yaml_config(config, output_path)

        assert output_path.exists()
        with open(output_path) as f:
            loaded = yaml.safe_load(f)
        assert loaded == config

    def test_saves_nested_config(self, temp_dir):
        """Should save nested configuration."""
        config = {
            "experiment": {
                "name": "test",
                "params": {
                    "a": 1,
                    "b": 2
                }
            }
        }
        output_path = temp_dir / "nested.yaml"

        save_yaml_config(config, output_path)

        with open(output_path) as f:
            loaded = yaml.safe_load(f)
        assert loaded == config

    def test_overwrites_existing_file(self, temp_dir):
        """Should overwrite existing file."""
        output_path = temp_dir / "existing.yaml"
        output_path.write_text("old: content")

        new_config = {"new": "content"}
        save_yaml_config(new_config, output_path)

        with open(output_path) as f:
            loaded = yaml.safe_load(f)
        assert loaded == new_config


class TestSaveJsonResults:
    """Tests for the save_json_results function."""

    def test_saves_results_to_json(self, temp_dir):
        """Should save results to JSON file."""
        results = {"accuracy": 0.95, "latency": 0.5}

        output_file = save_json_results(results, temp_dir, "test")

        assert output_file.exists()
        with open(output_file) as f:
            loaded = json.load(f)
        assert loaded == results

    def test_creates_output_directory(self, temp_dir):
        """Should create output directory if it doesn't exist."""
        nested_dir = temp_dir / "new" / "output" / "dir"
        results = {"test": True}

        save_json_results(results, nested_dir, "test")

        assert nested_dir.exists()

    def test_filename_has_timestamp(self, temp_dir):
        """Output filename should include timestamp."""
        results = {"test": True}

        output_file = save_json_results(results, temp_dir, "experiment")

        # Filename format: experiment_YYYYMMDD_HHMMSS.json
        assert output_file.name.startswith("experiment_")
        assert output_file.suffix == ".json"
        # Check timestamp format (should have 15 chars for YYYYMMDD_HHMMSS)
        timestamp_part = output_file.stem.replace("experiment_", "")
        assert len(timestamp_part) == 15  # YYYYMMDD_HHMMSS

    def test_handles_nested_dict(self, temp_dir):
        """Should handle nested dictionaries."""
        results = {
            "experiment": {
                "trials": [
                    {"id": 1, "result": 0.9},
                    {"id": 2, "result": 0.85}
                ]
            }
        }

        output_file = save_json_results(results, temp_dir, "nested")

        with open(output_file) as f:
            loaded = json.load(f)
        assert loaded == results

    def test_handles_non_serializable_with_default(self, temp_dir):
        """Should handle non-serializable objects with default serializer."""

        class CustomObj:
            def __str__(self):
                return "custom_obj"

        results = {"custom": CustomObj()}

        output_file = save_json_results(results, temp_dir, "custom")

        with open(output_file) as f:
            loaded = json.load(f)
        assert loaded["custom"] == "custom_obj"

    def test_returns_path_to_file(self, temp_dir):
        """Should return Path to created file."""
        results = {"test": True}

        output_file = save_json_results(results, temp_dir, "test")

        assert isinstance(output_file, Path)
        assert output_file.exists()
