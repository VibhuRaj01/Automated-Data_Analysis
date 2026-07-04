"""
report_builder_test.py

Automated tests for Module 7 -- Report Builder.

No LLM/network dependency at all -- this module is pure Python, so
these are ordinary pytest tests exercising real behavior (not mocks).
"""

import base64
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from report_builder.report_builder import (  # noqa: E402
    _image_to_data_uri,
    _insight_to_html,
    _resolve_chart_path,
    build_pdf_report,
    build_report,
)

# A valid 1x1 transparent PNG, used as a real chart fixture.
TINY_PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------


@pytest.fixture
def sample_profile():
    return {
        "profile_version": "1.0",
        "dataset": {"rows": 500, "columns": 3, "duplicates": 4, "memory_mb": 0.31},
        "columns": [
            {
                "name": "Revenue",
                "dtype": "float64",
                "missing": 2,
                "unique": 480,
                "semantic_type": "numeric",
                "statistics": {"mean": 245.8},
            },
            {
                "name": "Category",
                "dtype": "object",
                "missing": 0,
                "unique": 4,
                "semantic_type": "categorical",
                "statistics": {"top_values": {"A": 200}},
            },
            {
                "name": "Date",
                "dtype": "datetime64[ns]",
                "missing": 0,
                "unique": 500,
                "semantic_type": "datetime",
                "statistics": {"min": "2024-01-01", "max": "2025-01-01"},
            },
        ],
    }


@pytest.fixture
def project_with_chart(tmp_path):
    """A fake project root with a real chart PNG under outputs/graphs/."""
    graphs_dir = tmp_path / "outputs" / "graphs"
    graphs_dir.mkdir(parents=True)
    chart_path = graphs_dir / "graph_001.png"
    chart_path.write_bytes(TINY_PNG_BYTES)
    return tmp_path


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


# --------------------------------------------------------------------------
# _insight_to_html
# --------------------------------------------------------------------------


class TestInsightToHtml:
    def test_converts_bullets_to_list(self):
        text = "- Revenue grew steadily.\n- March saw a spike."
        html = _insight_to_html(text)
        assert html.startswith("<ul>")
        assert "<li>Revenue grew steadily.</li>" in html
        assert html.count("<li>") == 2

    def test_handles_star_and_dot_bullets(self):
        assert "<li>Point one</li>" in _insight_to_html("* Point one")
        assert "<li>Point one</li>" in _insight_to_html("\u2022 Point one")

    def test_returns_none_for_empty_input(self):
        assert _insight_to_html(None) is None
        assert _insight_to_html("") is None
        assert _insight_to_html("   ") is None

    def test_falls_back_to_paragraph_for_non_bullet_text(self):
        html = _insight_to_html("Just a plain sentence with no bullets here at all.")
        assert html.startswith("<p>")

    def test_escapes_html_special_characters(self):
        html = _insight_to_html("- Revenue < 100 & rising")
        assert "&lt;" in html
        assert "&amp;" in html
        assert "<script" not in html


# --------------------------------------------------------------------------
# _image_to_data_uri / _resolve_chart_path
# --------------------------------------------------------------------------


class TestImageHandling:
    def test_embeds_existing_png(self, project_with_chart):
        chart = project_with_chart / "outputs" / "graphs" / "graph_001.png"
        uri = _image_to_data_uri(chart)
        assert uri.startswith("data:image/png;base64,")

    def test_returns_none_for_missing_file(self, tmp_path):
        assert _image_to_data_uri(tmp_path / "nope.png") is None

    def test_resolves_relative_path_against_project_root(self, project_with_chart):
        resolved = _resolve_chart_path(
            "outputs/graphs/graph_001.png", project_with_chart
        )
        assert resolved.exists()

    def test_absolute_path_passed_through(self, project_with_chart):
        abs_path = project_with_chart / "outputs" / "graphs" / "graph_001.png"
        resolved = _resolve_chart_path(
            str(abs_path), Path("/completely/different/root")
        )
        assert resolved == abs_path


# --------------------------------------------------------------------------
# build_report (real render, no mocking needed -- pure Python module)
# --------------------------------------------------------------------------


class TestBuildReport:
    def test_produces_html_file(
        self, sample_profile, sample_analysis, project_with_chart, tmp_path
    ):
        items = [
            {
                "analysis": sample_analysis,
                "chart_path": "outputs/graphs/graph_001.png",
                "insight": "- Revenue grew 12% on average.",
            }
        ]
        out = build_report(
            sample_profile,
            items,
            output_dir=tmp_path / "reports",
            project_root=project_with_chart,
        )
        assert out.exists()
        assert out.suffix == ".html"

    def test_embeds_chart_as_data_uri_by_default(
        self, sample_profile, sample_analysis, project_with_chart, tmp_path
    ):
        items = [
            {
                "analysis": sample_analysis,
                "chart_path": "outputs/graphs/graph_001.png",
                "insight": "- x",
            }
        ]
        out = build_report(
            sample_profile,
            items,
            output_dir=tmp_path / "reports",
            project_root=project_with_chart,
        )
        html = out.read_text()
        assert "data:image/png;base64," in html

    def test_missing_chart_shows_placeholder_not_crash(
        self, sample_profile, sample_analysis, tmp_path
    ):
        items = [
            {
                "analysis": sample_analysis,
                "chart_path": "outputs/graphs/does_not_exist.png",
                "insight": "- x",
            }
        ]
        out = build_report(
            sample_profile,
            items,
            output_dir=tmp_path / "reports",
            project_root=tmp_path,
        )
        html = out.read_text()
        assert "Chart image not found" in html

    def test_missing_insight_shows_placeholder_not_crash(
        self, sample_profile, sample_analysis, project_with_chart, tmp_path
    ):
        items = [
            {
                "analysis": sample_analysis,
                "chart_path": "outputs/graphs/graph_001.png",
                "insight": None,
            }
        ]
        out = build_report(
            sample_profile,
            items,
            output_dir=tmp_path / "reports",
            project_root=project_with_chart,
        )
        html = out.read_text()
        assert "No insight text available" in html

    def test_items_sorted_by_priority(
        self, sample_profile, project_with_chart, tmp_path
    ):
        low_priority = {
            "priority": 3,
            "title": "Third",
            "analysis_type": "t",
            "chart": "bar",
            "columns": [],
            "reason": "",
        }
        high_priority = {
            "priority": 1,
            "title": "First",
            "analysis_type": "t",
            "chart": "bar",
            "columns": [],
            "reason": "",
        }
        items = [
            {
                "analysis": low_priority,
                "chart_path": "outputs/graphs/graph_001.png",
                "insight": "- a",
            },
            {
                "analysis": high_priority,
                "chart_path": "outputs/graphs/graph_001.png",
                "insight": "- b",
            },
        ]
        out = build_report(
            sample_profile,
            items,
            output_dir=tmp_path / "reports",
            project_root=project_with_chart,
        )
        html = out.read_text()
        assert html.index("First") < html.index("Third")

    def test_dataset_stats_rendered(
        self, sample_profile, sample_analysis, project_with_chart, tmp_path
    ):
        items = [
            {
                "analysis": sample_analysis,
                "chart_path": "outputs/graphs/graph_001.png",
                "insight": "- x",
            }
        ]
        out = build_report(
            sample_profile,
            items,
            output_dir=tmp_path / "reports",
            project_root=project_with_chart,
        )
        html = out.read_text()
        assert ">500<" in html  # row count
        assert "Revenue" in html
        assert "Category" in html

    def test_toc_links_to_each_section(
        self, sample_profile, sample_analysis, project_with_chart, tmp_path
    ):
        items = [
            {
                "analysis": sample_analysis,
                "chart_path": "outputs/graphs/graph_001.png",
                "insight": "- x",
            }
        ]
        out = build_report(
            sample_profile,
            items,
            output_dir=tmp_path / "reports",
            project_root=project_with_chart,
        )
        html = out.read_text()
        assert '<a href="#analysis-1">Revenue Trend</a>' in html

    def test_output_dir_created_if_missing(
        self, sample_profile, sample_analysis, project_with_chart, tmp_path
    ):
        target = tmp_path / "brand_new" / "nested" / "reports"
        assert not target.exists()
        build_report(
            sample_profile,
            [
                {
                    "analysis": sample_analysis,
                    "chart_path": "outputs/graphs/graph_001.png",
                    "insight": "- x",
                }
            ],
            output_dir=target,
            project_root=project_with_chart,
        )
        assert target.exists()

    def test_empty_report_items_still_renders(self, sample_profile, tmp_path):
        out = build_report(
            sample_profile, [], output_dir=tmp_path / "reports", project_root=tmp_path
        )
        assert out.exists()
        assert "Dataset Overview" in out.read_text()


# --------------------------------------------------------------------------
# build_pdf_report
# --------------------------------------------------------------------------


class TestBuildPdfReport:
    def test_raises_clear_error_without_weasyprint_installed(self, tmp_path):
        html_path = tmp_path / "report.html"
        html_path.write_text("<html><body>hi</body></html>")
        try:
            import weasyprint  # noqa: F401

            pytest.skip(
                "weasyprint is installed in this environment; skipping the not-installed case"
            )
        except ImportError:
            pass
        with pytest.raises(ImportError, match="WeasyPrint"):
            build_pdf_report(html_path)

    def test_raises_for_missing_html_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            build_pdf_report(tmp_path / "nope.html")
