import json

from llm.gemini import call_gemini
from generator.prompts import SYSTEM_PROMPT

GRAPH_COUNTER = 1


def generate_code(
    dataset_path: str,
    profile: dict,
    analysis: dict,
):

    global GRAPH_COUNTER

    filename = f"graph_{GRAPH_COUNTER:03}.png"

    user_prompt = f"""
Dataset Path

{dataset_path}

Dataset Profile

{json.dumps(profile, indent=2)}

Analysis

{json.dumps(analysis, indent=2)}

Output filename

outputs/graphs/{filename}
"""

    code = call_gemini(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.1,
        output_format="text/plain",
    )

    GRAPH_COUNTER += 1

    return code, filename
