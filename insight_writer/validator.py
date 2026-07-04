def validate_insight_output(response: str) -> str:
    """
    Validate and lightly clean the Insight Writer's raw LLM response.

    Mirrors the fail-fast style of planner/validator.py and
    generator/validator.py: raise ValueError on anything that violates
    the system prompt's output contract, otherwise return the cleaned text.
    """

    if response is None or not response.strip():
        raise ValueError("Insight Writer returned an empty response.")

    cleaned = response.strip()

    if cleaned.startswith("```") or cleaned.endswith("```"):
        raise ValueError(
            "Insight Writer output is wrapped in a Markdown code block; "
            "the system prompt requires raw bullet points."
        )

    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]

    if not lines:
        raise ValueError("Insight Writer returned no bullet points.")

    bullet_prefixes = ("-", "*", "\u2022")
    non_bullet_lines = [line for line in lines if not line.startswith(bullet_prefixes)]

    # Allow a little slack (e.g. a wrapped line continuing the previous bullet)
    # but reject responses that clearly ignored the bullet-point format.
    if len(non_bullet_lines) > len(lines) / 2:
        raise ValueError(
            "Insight Writer output does not look like bullet points "
            f"(first lines were: {lines[:2]!r})."
        )

    return cleaned
