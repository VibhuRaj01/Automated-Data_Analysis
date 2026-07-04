from __future__ import annotations

import json
from typing import Any, Optional

from llm.gemini import call_gemini

from insight_writer.prompts import SYSTEM_PROMPT
from insight_writer.validator import validate_insight_output

STATS_MARKER = "STATS_JSON:"


def _extract_computed_metrics(stdout: str) -> Optional[dict[str, Any]]:
    """
    Pull the STATS_JSON:{...} payload a generated script printed, if any.

    Generated code (per generator/prompts.py) is required to print exactly
    one line of the form `STATS_JSON:{...}` as its last line of output.
    Older scripts generated before this contract existed won't have one --
    in that case we return None and Insight Writer falls back to
    profile-only grounding rather than failing outright.
    """
    if not stdout:
        return None

    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith(STATS_MARKER):
            payload = line[len(STATS_MARKER) :].strip()
            try:
                parsed = json.loads(payload)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
    return None


def _select_column_profiles(profile: dict, columns_used: list[str]) -> list[dict]:
    """Filter the full dataset profile down to just the columns this analysis touched."""
    return [c for c in profile.get("columns", []) if c.get("name") in columns_used]


def generate_insight(
    profile: dict,
    analysis: dict,
    execution_result: dict,
) -> str:
    """
    Turn a completed analysis run into bullet-point, business-relevant insights.

    Parameters
    ----------
    profile : dict
        Dataset profile from profiler.profile_dataset().
    analysis : dict
        The planned analysis item from planner.generate_analysis_plan()
        (keys: priority, title, analysis_type, chart, columns, reason).
    execution_result : dict
        The dict returned by executor.execute_script() for the script that
        produced this analysis's chart (post-debugger repair, if any repair
        was needed). Must reflect a successful run.

    Returns
    -------
    str
        Cleaned, bullet-point insight text ready to embed in the report.

    Raises
    ------
    ValueError
        If execution_result indicates the analysis did not succeed, or if
        the LLM's response fails output validation.
    """

    if not execution_result.get("success"):
        raise ValueError(
            "generate_insight() was called with a failed execution_result. "
            "Only successfully executed analyses should reach the Insight Writer -- "
            "route failures through the Debugger first."
        )

    columns_used = analysis.get("columns", [])
    column_profiles = _select_column_profiles(profile, columns_used)
    computed_metrics = _extract_computed_metrics(execution_result.get("stdout", ""))

    objective = {
        "title": analysis.get("title"),
        "analysis_type": analysis.get("analysis_type"),
        "chart_type": analysis.get("chart"),
        "reason": analysis.get("reason"),
        "columns_used": columns_used,
    }

    metrics_section = (
        "(not captured -- base insights on column profiles and objective only, "
        "keep specific figures qualitative)"
        if computed_metrics is None
        else json.dumps(computed_metrics, indent=2, default=str)
    )

    user_prompt = f"""
Analysis Objective

{json.dumps(objective, indent=2)}

Relevant Column Profiles

{json.dumps(column_profiles, indent=2, default=str)}

Computed Metrics From Execution

{metrics_section}

Dataset Summary

{json.dumps(profile.get("dataset", {}), indent=2)}
"""

    response = call_gemini(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.3,
        output_format="text/plain",
    )

    return validate_insight_output(response)
