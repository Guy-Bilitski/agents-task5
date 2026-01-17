"""
Unit Tests for Data Module.

Tests for data generation and manipulation utilities.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common.data import generate_text_block, insert_needle, TEMPLATES
from common.utils import set_seed


class TestTemplates:
    """Tests for the TEMPLATES constant."""

    def test_templates_has_expected_domains(self):
        """TEMPLATES should have all expected domains."""
        expected_domains = ["generic", "medicine", "law", "tech"]
        for domain in expected_domains:
            assert domain in TEMPLATES

    def test_templates_domains_have_content(self):
        """Each domain should have template sentences."""
        for domain, templates in TEMPLATES.items():
            assert isinstance(templates, list)
            assert len(templates) > 0
            for template in templates:
                assert isinstance(template, str)
                assert len(template) > 0

    def test_templates_are_complete_sentences(self):
        """Templates should be complete sentences (end with period)."""
        for domain, templates in TEMPLATES.items():
            for template in templates:
                assert template.endswith(".")


class TestGenerateTextBlock:
    """Tests for the generate_text_block function."""

    def test_returns_string(self):
        """generate_text_block should return a string."""
        result = generate_text_block()
        assert isinstance(result, str)

    def test_meets_minimum_word_count(self):
        """Generated text should meet minimum word count."""
        min_words = 100
        result = generate_text_block(min_words=min_words)
        word_count = len(result.split())
        # Should be exactly min_words (the function slices to min_words)
        assert word_count == min_words

    def test_different_min_words(self):
        """Should respect different min_words values."""
        for min_words in [50, 100, 200, 500]:
            result = generate_text_block(min_words=min_words)
            word_count = len(result.split())
            assert word_count == min_words

    def test_uses_generic_domain_by_default(self):
        """Should use generic domain by default."""
        set_seed(42)
        result = generate_text_block(min_words=50)

        # Should contain words from generic templates
        generic_words = set()
        for template in TEMPLATES["generic"]:
            generic_words.update(template.lower().split())

        result_words = set(result.lower().split())
        assert len(result_words.intersection(generic_words)) > 0

    def test_uses_specified_domain(self):
        """Should use specified domain templates."""
        set_seed(42)

        # Medicine domain should have different vocabulary
        result = generate_text_block(domain="medicine", min_words=200)
        result_lower = result.lower()

        # Should contain medicine-specific terms
        medicine_terms = ["clinical", "patient", "surgery", "vaccines", "health"]
        found_terms = [term for term in medicine_terms if term in result_lower]
        assert len(found_terms) > 0

    def test_unknown_domain_falls_back_to_generic(self):
        """Unknown domain should fall back to generic."""
        set_seed(42)
        result = generate_text_block(domain="nonexistent", min_words=50)

        # Should still work and produce text
        assert len(result) > 0
        assert len(result.split()) == 50

    def test_reproducible_with_seed(self):
        """Should be reproducible with same seed."""
        set_seed(42)
        result1 = generate_text_block(min_words=100)

        set_seed(42)
        result2 = generate_text_block(min_words=100)

        assert result1 == result2

    def test_different_with_different_seed(self):
        """Should produce different results with different seeds."""
        set_seed(42)
        result1 = generate_text_block(min_words=100)

        set_seed(123)
        result2 = generate_text_block(min_words=100)

        # Very likely to be different
        assert result1 != result2


class TestInsertNeedle:
    """Tests for the insert_needle function."""

    def test_inserts_needle_into_text(self):
        """Should insert needle into text."""
        text = "The quick brown fox jumps over the lazy dog"
        needle = "NEEDLE"

        result = insert_needle(text, needle, position="middle")

        assert needle in result
        assert "quick" in result
        assert "dog" in result

    def test_insert_at_start(self):
        """Should insert needle near start with position='start'."""
        text = "word " * 100  # 100 words
        needle = "NEEDLE"

        result = insert_needle(text, needle, position="start")
        words = result.split()

        needle_index = words.index("NEEDLE")
        # Should be at ~10% position
        assert needle_index < 20  # Near the beginning

    def test_insert_at_middle(self):
        """Should insert needle near middle with position='middle'."""
        text = "word " * 100  # 100 words
        needle = "NEEDLE"

        result = insert_needle(text, needle, position="middle")
        words = result.split()

        needle_index = words.index("NEEDLE")
        # Should be at ~50% position
        assert 40 < needle_index < 60

    def test_insert_at_end(self):
        """Should insert needle near end with position='end'."""
        text = "word " * 100  # 100 words
        needle = "NEEDLE"

        result = insert_needle(text, needle, position="end")
        words = result.split()

        needle_index = words.index("NEEDLE")
        # Should be at ~90% position
        assert needle_index > 80

    def test_insert_at_float_position(self):
        """Should insert needle at specified float position."""
        text = "word " * 100  # 100 words
        needle = "NEEDLE"

        result = insert_needle(text, needle, position=0.25)
        words = result.split()

        needle_index = words.index("NEEDLE")
        # Should be at ~25% position
        assert 20 < needle_index < 30

    def test_insert_at_random_position(self):
        """Should insert at random position with position='random'."""
        set_seed(42)
        text = "word " * 100
        needle = "NEEDLE"

        result = insert_needle(text, needle, position="random")

        assert needle in result

    def test_preserves_original_words(self):
        """Should preserve all original words."""
        original_words = ["apple", "banana", "cherry", "date", "elderberry"]
        text = " ".join(original_words)
        needle = "NEEDLE"

        result = insert_needle(text, needle, position="middle")
        result_words = result.split()

        for word in original_words:
            assert word in result_words

    def test_increases_word_count_by_one(self):
        """Should increase word count by one (the needle)."""
        text = "one two three four five"
        original_count = len(text.split())
        needle = "NEEDLE"

        result = insert_needle(text, needle, position="middle")
        new_count = len(result.split())

        assert new_count == original_count + 1

    def test_handles_empty_text(self):
        """Should handle empty text."""
        text = ""
        needle = "NEEDLE"

        result = insert_needle(text, needle, position="middle")

        assert result == "NEEDLE"

    def test_handles_single_word_text(self):
        """Should handle single word text."""
        text = "word"
        needle = "NEEDLE"

        result = insert_needle(text, needle, position="middle")

        assert "NEEDLE" in result
        assert "word" in result

    def test_position_clamped_to_bounds(self):
        """Float position should be clamped to valid bounds."""
        text = "word " * 10
        needle = "NEEDLE"

        # Position > 1.0 should be clamped
        result1 = insert_needle(text, needle, position=2.0)
        assert needle in result1

        # Position < 0.0 should be clamped
        result2 = insert_needle(text, needle, position=-0.5)
        assert needle in result2

    def test_multi_word_needle(self):
        """Should handle multi-word needle."""
        text = "The quick brown fox"
        needle = "secret code 12345"

        result = insert_needle(text, needle, position="middle")

        # Multi-word needle is inserted as single "word" at position
        assert "secret code 12345" in result


class TestDataIntegration:
    """Integration tests for data generation."""

    def test_generate_and_insert_workflow(self):
        """Test typical workflow of generating text and inserting needle."""
        set_seed(42)

        # Generate text
        text = generate_text_block(domain="tech", min_words=200)
        assert len(text.split()) == 200

        # Insert needle
        needle = "The API key is XYZ123."
        haystack = insert_needle(text, needle, position="middle")

        # Verify
        assert needle in haystack
        assert len(haystack.split()) == 201

    def test_multiple_needles_at_different_positions(self):
        """Test inserting multiple needles at different positions."""
        set_seed(42)

        text = generate_text_block(min_words=300)

        # Insert first needle
        needle1 = "FIRST_NEEDLE"
        text = insert_needle(text, needle1, position="start")

        # Insert second needle
        needle2 = "SECOND_NEEDLE"
        text = insert_needle(text, needle2, position="end")

        words = text.split()
        idx1 = words.index("FIRST_NEEDLE")
        idx2 = words.index("SECOND_NEEDLE")

        # First needle should be before second
        assert idx1 < idx2

    def test_reproducibility_of_full_workflow(self):
        """Full workflow should be reproducible with same seed."""
        def run_workflow():
            set_seed(42)
            text = generate_text_block(domain="law", min_words=150)
            needle = "The verdict is GUILTY."
            return insert_needle(text, needle, position=0.6)

        result1 = run_workflow()
        result2 = run_workflow()

        assert result1 == result2
