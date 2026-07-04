import json

from planner.prompts import SYSTEM_PROMPT
from planner.validator import validate_llm_output

from llm.gemini import call_gemini


def generate_analysis_plan(profile: dict):

    profile_text = json.dumps(
        profile,
        indent=2,
    )

    user_prompt = f"""
Dataset Profile

{profile_text}
"""

    response = call_gemini(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        output_format="application/json",
    )

    return validate_llm_output(response)
