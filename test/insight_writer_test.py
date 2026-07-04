"""
insight_writer_test.py

These tests mock call_gemini so the module's logic -- STATS_JSON extraction, column
filtering, prompt assembly, and output validation -- can be verified
without network access or an API key.

Run with: pytest test/insight_writer_test.py -v
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# llm/gemini.py raises EnvironmentError at import time if GEMINI_API is
# unset, and requires the google-genai client to construct. Set a dummy
# key before any import in this file pulls that module in transitively.
os.environ.setdefault("GEMINI_API", "dummy-key-for-tests")

from insight_writer.insight_writer import (  # noqa: E402
    _extract_computed_metrics,
    _select_column_profiles,
    generate_insight,
)
from insight_writer.validator import validate_insight_output  # noqa: E402

# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------


@pytest.fixture
def sample_profile():
    return {
        "dataset": {"rows": 500, "columns": 5, "duplicates": 3, "memory_mb": 0.4},
        "columns": [
            {
                "name": "Revenue",
                "dtype": "float64",
                "semantic_type": "numeric",
                "missing": 2,
                "unique": 480,
                "statistics": {"mean": 245.8, "std": 41.3},
            },
            {
                "name": "Category",
                "dtype": "object",
                "semantic_type": "categorical",
                "missing": 0,
                "unique": 4,
                "statistics": {"top_values": {"A": 200, "B": 150}},
            },
            {
                "name": "Date",
                "dtype": "datetime64[ns]",
                "semantic_type": "datetime",
                "missing": 0,
                "unique": 500,
                "statistics": {"min": "2024-01-01", "max": "2025-05-15"},
            },
        ],
    }


@pytest.fixture
def sample_analysis():
    return {
        "priority": 1,
        "title": "Revenue Trend",
        "analysis_type": "trend",
        "chart": "line",
        "columns": ["Date", "Revenue"],
        "reason": "Understand long-term growth.",
    }


@pytest.fixture
def success_result_with_stats():
    return {
        "success": True,
        "return_code": 0,
        "stdout": 'Some progress line\nSTATS_JSON:{"mean_revenue": 245.8, "growth_pct": 12.4}\n',
        "stderr": "",
        "execution_time": 0.5,
    }


@pytest.fixture
def success_result_without_stats():
    # Simulates an older script generated before the STATS_JSON contract existed.
    return {
        "success": True,
        "return_code": 0,
        "stdout": "",
        "stderr": "",
        "execution_time": 0.5,
    }


@pytest.fixture
def failed_result():
    return {
        "success": False,
        "return_code": 1,
        "stdout": "",
        "stderr": "KeyError: 'Revenue'",
        "execution_time": 0.1,
    }


# --------------------------------------------------------------------------
# _extract_computed_metrics
# --------------------------------------------------------------------------


class TestExtractComputedMetrics:
    def test_extracts_valid_stats_line(self):
        stdout = 'STATS_JSON:{"mean": 1.5, "count": 10}'
        assert _extract_computed_metrics(stdout) == {"mean": 1.5, "count": 10}

    def test_finds_marker_among_other_output(self):
        stdout = 'loading data\ncomputing stats\nSTATS_JSON:{"a": 1}\n'
        assert _extract_computed_metrics(stdout) == {"a": 1}

    def test_returns_none_for_empty_stdout(self):
        assert _extract_computed_metrics("") is None
        assert _extract_computed_metrics(None) is None

    def test_returns_none_when_marker_absent(self):
        assert _extract_computed_metrics("just some regular output\n") is None

    def test_skips_malformed_json_and_keeps_looking(self):
        stdout = 'STATS_JSON:{not valid json}\nSTATS_JSON:{"a": 2}\n'
        assert _extract_computed_metrics(stdout) == {"a": 2}

    def test_marker_not_at_line_start_is_ignored(self):
        stdout = 'prefix STATS_JSON:{"a": 1}'
        assert _extract_computed_metrics(stdout) is None

    def test_non_dict_payload_is_rejected(self):
        stdout = "STATS_JSON:[1, 2, 3]"
        assert _extract_computed_metrics(stdout) is None


# --------------------------------------------------------------------------
# _select_column_profiles
# --------------------------------------------------------------------------


class TestSelectColumnProfiles:
    def test_filters_to_requested_columns(self, sample_profile):
        result = _select_column_profiles(sample_profile, ["Date", "Revenue"])
        names = {c["name"] for c in result}
        assert names == {"Date", "Revenue"}

    def test_missing_column_name_yields_empty(self, sample_profile):
        assert _select_column_profiles(sample_profile, ["Nonexistent"]) == []

    def test_empty_column_list_yields_empty(self, sample_profile):
        assert _select_column_profiles(sample_profile, []) == []


# --------------------------------------------------------------------------
# validate_insight_output
# --------------------------------------------------------------------------


class TestValidateInsightOutput:
    def test_accepts_clean_bullets(self):
        text = "- Revenue grew steadily.\n- March had a spike."
        assert validate_insight_output(text) == text

    def test_rejects_empty_response(self):
        with pytest.raises(ValueError):
            validate_insight_output("")
        with pytest.raises(ValueError):
            validate_insight_output("   ")

    def test_rejects_markdown_fence(self):
        with pytest.raises(ValueError):
            validate_insight_output("```\n- point one\n```")

    def test_rejects_prose_without_bullets(self):
        with pytest.raises(ValueError):
            validate_insight_output(
                "This is just a paragraph of prose with no bullet points at all "
                "explaining the analysis in long form sentences."
            )

    def test_tolerates_a_minority_of_non_bullet_lines(self):
        # e.g. a wrapped continuation line -- shouldn't be over-strict
        text = "- Revenue grew steadily across Q2\n  continuing into Q3.\n- Category A leads."
        assert validate_insight_output(text) == text


# --------------------------------------------------------------------------
# generate_insight (mocking the LLM call)
# --------------------------------------------------------------------------


class TestGenerateInsight:
    def test_raises_on_failed_execution(
        self, sample_profile, sample_analysis, failed_result
    ):
        with pytest.raises(ValueError, match="failed execution_result"):
            generate_insight(sample_profile, sample_analysis, failed_result)

    def test_does_not_call_llm_on_failed_execution(
        self, sample_profile, sample_analysis, failed_result
    ):
        with patch("insight_writer.insight_writer.call_gemini") as mock_call:
            with pytest.raises(ValueError):
                generate_insight(sample_profile, sample_analysis, failed_result)
            mock_call.assert_not_called()

    def test_happy_path_returns_llm_text(
        self, sample_profile, sample_analysis, success_result_with_stats
    ):
        with patch("insight_writer.insight_writer.call_gemini") as mock_call:
            mock_call.return_value = (
                "- Revenue grew 12.4% on average.\n- Growth accelerated after March."
            )
            result = generate_insight(
                sample_profile, sample_analysis, success_result_with_stats
            )
        assert result.startswith("- Revenue grew")
        mock_call.assert_called_once()

    def test_prompt_includes_computed_metrics_when_present(
        self, sample_profile, sample_analysis, success_result_with_stats
    ):
        with patch("insight_writer.insight_writer.call_gemini") as mock_call:
            mock_call.return_value = "- Insight."
            generate_insight(sample_profile, sample_analysis, success_result_with_stats)
        _, kwargs = mock_call.call_args
        assert "growth_pct" in kwargs["user_prompt"]
        assert "12.4" in kwargs["user_prompt"]

    def test_prompt_flags_missing_metrics_gracefully(
        self, sample_profile, sample_analysis, success_result_without_stats
    ):
        with patch("insight_writer.insight_writer.call_gemini") as mock_call:
            mock_call.return_value = "- Insight."
            generate_insight(
                sample_profile, sample_analysis, success_result_without_stats
            )
        _, kwargs = mock_call.call_args
        assert "not captured" in kwargs["user_prompt"]

    def test_prompt_only_includes_relevant_columns(
        self, sample_profile, sample_analysis, success_result_with_stats
    ):
        # sample_analysis only uses Date and Revenue -- Category should not appear
        with patch("insight_writer.insight_writer.call_gemini") as mock_call:
            mock_call.return_value = "- Insight."
            generate_insight(sample_profile, sample_analysis, success_result_with_stats)
        _, kwargs = mock_call.call_args
        assert '"Category"' not in kwargs["user_prompt"]
        assert '"Revenue"' in kwargs["user_prompt"]

    def test_propagates_validation_error_from_bad_llm_output(
        self, sample_profile, sample_analysis, success_result_with_stats
    ):
        with patch("insight_writer.insight_writer.call_gemini") as mock_call:
            mock_call.return_value = "```\n- fenced output\n```"
            with pytest.raises(ValueError):
                generate_insight(
                    sample_profile, sample_analysis, success_result_with_stats
                )

    def test_uses_low_ish_temperature(
        self, sample_profile, sample_analysis, success_result_with_stats
    ):
        with patch("insight_writer.insight_writer.call_gemini") as mock_call:
            mock_call.return_value = "- Insight."
            generate_insight(sample_profile, sample_analysis, success_result_with_stats)
        _, kwargs = mock_call.call_args
        assert kwargs["temperature"] <= 0.5
