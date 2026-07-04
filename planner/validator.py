import json


def validate_llm_output(response: str):

    try:
        parsed = json.loads(response)

    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON.\n{e}")

    if not isinstance(parsed, list):
        raise ValueError("Expected a list of analyses.")

    required = {
        "priority",
        "title",
        "analysis_type",
        "chart",
        "columns",
        "reason",
    }

    for analysis in parsed:
        missing = required - analysis.keys()
        if missing:
            raise ValueError(f"Missing fields: {missing}")

    return parsed
