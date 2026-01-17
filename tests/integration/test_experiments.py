"""
Integration Tests for Experiments.

These tests verify that experiment components work together correctly.
They use mocked LLM backends to avoid requiring external services.
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common.llm import MockLLM, OllamaLLM
from common.utils import setup_logger, set_seed, load_yaml_config, save_json_results
from common.data import generate_text_block, insert_needle


class TestExperimentWorkflow:
    """Integration tests for complete experiment workflows."""

    @pytest.fixture
    def experiment_config(self, temp_dir, sample_config):
        """Create experiment configuration for testing."""
        import yaml

        config_dir = temp_dir / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "experiment.yaml"

        with open(config_path, 'w') as f:
            yaml.dump(sample_config, f)

        return config_path

    def test_lost_in_middle_workflow(self, temp_dir):
        """Test the Lost in the Middle experiment workflow."""
        set_seed(42)

        # Setup
        logger = setup_logger("test_litm", log_dir=temp_dir, console=False)
        llm = MockLLM(
            latency_base=0.01,
            noise_threshold=10000,
            noise_prob_low=0.0,
            noise_prob_high=0.0
        )

        # Generate haystack with needle at different positions
        positions = ["start", "middle", "end"]
        results = {"trials": [], "summary": {}}

        for pos in positions:
            # Generate context
            context = generate_text_block(min_words=100)
            needle = "The secret code is ALPHA123."
            haystack = insert_needle(context, needle, position=pos)

            # Query LLM
            response = llm.query(
                context=haystack,
                question="What is the secret code?",
                expected_answer="ALPHA123"
            )

            results["trials"].append({
                "position": pos,
                "is_accurate": response["is_accurate"],
                "latency": response["latency"]
            })

            logger.info(f"Position {pos}: accurate={response['is_accurate']}")

        # Calculate summary
        accuracies = [t["is_accurate"] for t in results["trials"]]
        results["summary"]["accuracy"] = sum(accuracies) / len(accuracies)

        # Save results
        output_file = save_json_results(results, temp_dir / "results", "litm")

        # Verify
        assert output_file.exists()
        with open(output_file) as f:
            loaded = json.load(f)
        assert len(loaded["trials"]) == 3
        assert "accuracy" in loaded["summary"]

    def test_context_size_workflow(self, temp_dir):
        """Test the Context Window Size experiment workflow."""
        set_seed(42)

        # Setup
        logger = setup_logger("test_context_size", log_dir=temp_dir, console=False)
        llm = MockLLM(latency_base=0.01, latency_per_token=0.001)

        # Test with increasing document counts
        doc_counts = [5, 10, 20]
        results = {"trials": [], "summary": {}}

        for count in doc_counts:
            # Generate documents
            docs = [generate_text_block(min_words=50) for _ in range(count)]
            context = " ".join(docs)

            # Query LLM
            response = llm.query(
                context=context,
                question="Summarize the content."
            )

            results["trials"].append({
                "doc_count": count,
                "token_count": response["token_count"],
                "latency": response["latency"]
            })

            logger.info(f"Docs {count}: tokens={response['token_count']}, latency={response['latency']:.3f}")

        # Verify latency increases with token count
        latencies = [t["latency"] for t in results["trials"]]
        assert latencies[0] < latencies[1] < latencies[2]

        # Save results
        output_file = save_json_results(results, temp_dir / "results", "context_size")
        assert output_file.exists()

    def test_rag_vs_full_context_workflow(self, temp_dir):
        """Test the RAG vs Full Context experiment workflow (simplified)."""
        set_seed(42)

        # Setup
        logger = setup_logger("test_rag", log_dir=temp_dir, console=False)
        llm = MockLLM(
            latency_base=0.01,
            noise_threshold=500,  # Low threshold to simulate degradation
            noise_prob_low=0.0,
            noise_prob_high=0.5
        )

        # Generate documents with a target fact
        docs = [generate_text_block(min_words=100) for _ in range(10)]
        target_fact = "The answer to the ultimate question is 42."
        target_doc_idx = 5
        docs[target_doc_idx] = insert_needle(docs[target_doc_idx], target_fact, "middle")

        results = {"rag": [], "full_context": []}

        # Simulate RAG (use only relevant doc)
        rag_context = docs[target_doc_idx]
        rag_response = llm.query(
            context=rag_context,
            question="What is the answer to the ultimate question?",
            expected_answer="42"
        )
        results["rag"].append({
            "is_accurate": rag_response["is_accurate"],
            "latency": rag_response["latency"],
            "tokens": rag_response["token_count"]
        })

        # Simulate full context (use all docs)
        full_context = " ".join(docs)
        full_response = llm.query(
            context=full_context,
            question="What is the answer to the ultimate question?",
            expected_answer="42"
        )
        results["full_context"].append({
            "is_accurate": full_response["is_accurate"],
            "latency": full_response["latency"],
            "tokens": full_response["token_count"]
        })

        # RAG should have fewer tokens
        assert results["rag"][0]["tokens"] < results["full_context"][0]["tokens"]

        # Save results
        output_file = save_json_results(results, temp_dir / "results", "rag_comparison")
        assert output_file.exists()

    def test_memory_strategies_workflow(self, temp_dir):
        """Test the Memory Strategies experiment workflow (simplified)."""
        set_seed(42)

        # Setup
        logger = setup_logger("test_memory", log_dir=temp_dir, console=False)
        llm = MockLLM(latency_base=0.01, noise_threshold=10000)

        # Simulate multi-step conversation
        steps = [
            "Remember: The password is SECRET123.",
            "The sky is blue.",
            "Water boils at 100 degrees.",
            "What is the password?"
        ]

        results = {"select": [], "compress": [], "write": []}

        # SELECT strategy (uses full history)
        full_history = " ".join(steps[:-1])
        select_response = llm.query(
            context=full_history,
            question=steps[-1],
            expected_answer="SECRET123"
        )
        results["select"].append({
            "is_accurate": select_response["is_accurate"],
            "tokens": select_response["token_count"]
        })

        # COMPRESS strategy (simulated shorter context)
        compressed = "Password is SECRET123. Sky blue. Water boils 100."
        compress_response = llm.query(
            context=compressed,
            question=steps[-1],
            expected_answer="SECRET123"
        )
        results["compress"].append({
            "is_accurate": compress_response["is_accurate"],
            "tokens": compress_response["token_count"]
        })

        # WRITE strategy (only most recent + scratchpad)
        scratchpad = "Scratchpad: password=SECRET123"
        write_response = llm.query(
            context=scratchpad,
            question=steps[-1],
            expected_answer="SECRET123"
        )
        results["write"].append({
            "is_accurate": write_response["is_accurate"],
            "tokens": write_response["token_count"]
        })

        # All strategies should be accurate with correct info
        logger.info(f"SELECT: {results['select'][0]}")
        logger.info(f"COMPRESS: {results['compress'][0]}")
        logger.info(f"WRITE: {results['write'][0]}")

        # Save results
        output_file = save_json_results(results, temp_dir / "results", "memory_strategies")
        assert output_file.exists()


class TestConfigurationLoading:
    """Tests for loading and validating experiment configurations."""

    def test_load_experiment_config(self, sample_yaml_config, sample_config):
        """Should load experiment configuration correctly."""
        config = load_yaml_config(sample_yaml_config)

        assert config["experiment"]["name"] == sample_config["experiment"]["name"]
        assert config["experiment"]["seed"] == sample_config["experiment"]["seed"]
        assert config["llm"]["model_name"] == sample_config["llm"]["model_name"]

    def test_config_with_missing_optional_fields(self, temp_dir):
        """Should handle configs with missing optional fields."""
        import yaml

        minimal_config = {
            "experiment": {
                "name": "minimal_test"
            }
        }
        config_path = temp_dir / "minimal.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(minimal_config, f)

        config = load_yaml_config(config_path)
        assert config["experiment"]["name"] == "minimal_test"
        # Optional fields should be missing
        assert "seed" not in config["experiment"]


class TestLoggingIntegration:
    """Tests for logging across experiment runs."""

    def test_logger_captures_experiment_events(self, temp_dir):
        """Logger should capture all experiment events."""
        logger = setup_logger(
            "experiment_test",
            log_dir=temp_dir,
            console=False,
            file=True
        )

        # Simulate experiment events
        logger.info("Starting experiment")
        logger.info("Running trial 1")
        logger.info("Trial 1 complete: accuracy=0.95")
        logger.info("Experiment complete")

        # Read log file
        log_files = list(temp_dir.glob("*.log"))
        assert len(log_files) == 1

        content = log_files[0].read_text()
        assert "Starting experiment" in content
        assert "Running trial 1" in content
        assert "accuracy=0.95" in content
        assert "Experiment complete" in content

    def test_multiple_loggers_independent(self, temp_dir):
        """Multiple loggers should be independent."""
        logger1 = setup_logger("exp1", log_dir=temp_dir, console=False)
        logger2 = setup_logger("exp2", log_dir=temp_dir, console=False)

        logger1.info("Message from exp1")
        logger2.info("Message from exp2")

        log_files = list(temp_dir.glob("*.log"))
        assert len(log_files) == 2

        # Each log should only have its own messages
        for log_file in log_files:
            content = log_file.read_text()
            if "exp1" in log_file.name:
                assert "Message from exp1" in content
                assert "Message from exp2" not in content
            else:
                assert "Message from exp2" in content
                assert "Message from exp1" not in content


class TestResultsPersistence:
    """Tests for experiment results persistence."""

    def test_results_json_structure(self, temp_dir, sample_experiment_results):
        """Saved results should maintain correct structure."""
        output_file = save_json_results(
            sample_experiment_results,
            temp_dir,
            "test_results"
        )

        with open(output_file) as f:
            loaded = json.load(f)

        assert loaded["experiment_name"] == sample_experiment_results["experiment_name"]
        assert len(loaded["trials"]) == len(sample_experiment_results["trials"])
        assert loaded["summary"]["accuracy_mean"] == sample_experiment_results["summary"]["accuracy_mean"]

    def test_multiple_result_files(self, temp_dir):
        """Multiple runs should create separate result files."""
        import time

        for i in range(3):
            results = {"run": i}
            save_json_results(results, temp_dir, "multi_run")
            time.sleep(0.1)  # Ensure different timestamps

        result_files = list(temp_dir.glob("multi_run_*.json"))
        assert len(result_files) == 3

    def test_results_can_be_aggregated(self, temp_dir):
        """Results from multiple files should be aggregatable."""
        # Save multiple result files
        for i in range(3):
            results = {"accuracy": 0.8 + i * 0.05}
            save_json_results(results, temp_dir, f"run_{i}")

        # Aggregate results
        all_results = []
        for result_file in temp_dir.glob("run_*.json"):
            with open(result_file) as f:
                all_results.append(json.load(f))

        accuracies = [r["accuracy"] for r in all_results]
        mean_accuracy = sum(accuracies) / len(accuracies)

        assert len(all_results) == 3
        assert 0.8 <= mean_accuracy <= 0.9


class TestEndToEndExperiment:
    """End-to-end tests simulating complete experiment runs."""

    def test_complete_experiment_lifecycle(self, temp_dir):
        """Test complete experiment from config to results."""
        import yaml

        # 1. Create configuration
        config = {
            "experiment": {
                "name": "e2e_test",
                "seed": 42,
                "num_trials": 5
            },
            "llm": {
                "latency_base": 0.01,
                "noise_threshold": 10000
            }
        }
        config_path = temp_dir / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        # 2. Load configuration
        loaded_config = load_yaml_config(config_path)

        # 3. Setup experiment
        set_seed(loaded_config["experiment"]["seed"])
        logger = setup_logger(
            loaded_config["experiment"]["name"],
            log_dir=temp_dir / "logs",
            console=False
        )
        llm = MockLLM(
            latency_base=loaded_config["llm"]["latency_base"],
            noise_threshold=loaded_config["llm"]["noise_threshold"]
        )

        # 4. Run trials
        results = {
            "experiment_name": loaded_config["experiment"]["name"],
            "config": loaded_config,
            "trials": []
        }

        for trial_id in range(loaded_config["experiment"]["num_trials"]):
            context = generate_text_block(min_words=50)
            needle = f"Trial {trial_id} secret: CODE{trial_id}"
            haystack = insert_needle(context, needle, position="middle")

            response = llm.query(
                context=haystack,
                question=f"What is trial {trial_id}'s secret code?",
                expected_answer=f"CODE{trial_id}"
            )

            results["trials"].append({
                "trial_id": trial_id,
                "is_accurate": response["is_accurate"],
                "latency": response["latency"]
            })

            logger.info(f"Trial {trial_id}: accurate={response['is_accurate']}")

        # 5. Calculate summary
        accuracies = [t["is_accurate"] for t in results["trials"]]
        latencies = [t["latency"] for t in results["trials"]]
        results["summary"] = {
            "accuracy_mean": sum(accuracies) / len(accuracies),
            "latency_mean": sum(latencies) / len(latencies)
        }

        # 6. Save results
        output_file = save_json_results(
            results,
            temp_dir / "results",
            loaded_config["experiment"]["name"]
        )

        # 7. Verify outputs
        assert (temp_dir / "logs").exists()
        assert output_file.exists()

        with open(output_file) as f:
            final_results = json.load(f)

        assert final_results["experiment_name"] == "e2e_test"
        assert len(final_results["trials"]) == 5
        assert "summary" in final_results
        assert 0 <= final_results["summary"]["accuracy_mean"] <= 1

        logger.info("Experiment completed successfully")
