FORBIDDEN = [
    "input(",
    "exec(",
    "eval(",
    "subprocess",
    "socket",
    "requests",
    "os.system",
]


def validate_code(code: str):

    for forbidden in FORBIDDEN:

        if forbidden in code:
            raise ValueError(f"Forbidden statement detected: {forbidden}")

    if "plt.savefig" not in code:
        raise ValueError("Generated code does not save the figure.")

    if "import pandas" not in code:
        raise ValueError("pandas import missing.")

    if "import json" not in code:
        raise ValueError("json import missing (required for STATS_JSON output).")

    if "STATS_JSON:" not in code:
        raise ValueError(
            "Generated code does not print a STATS_JSON: summary line. "
            "The Insight Writer requires computed metrics from execution."
        )

    if code.count("STATS_JSON:") > 1:
        raise ValueError(
            "Generated code prints STATS_JSON: more than once; exactly one summary line is required."
        )

    return True
