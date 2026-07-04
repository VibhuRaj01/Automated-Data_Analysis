import json

from llm.gemini import call_gemini

from debugger.prompts import SYSTEM_PROMPT
from generator.validator import validate_code


def repair_code(
    original_code: str,
    profile: dict,
    analysis: dict,
    execution_result: dict,
):
    """
    Repair Python code using an LLM.

    Parameters
    ----------
    original_code : str
    profile : dict
    analysis : dict
    execution_result : dict

    Returns
    -------
    str
        Repaired Python code.
    """

    user_prompt = f"""
Dataset Profile

{json.dumps(profile, indent=2)}

Analysis

{json.dumps(analysis, indent=2)}

Original Code

{original_code}

Execution Result

Return Code:
{execution_result['return_code']}

STDOUT:
{execution_result['stdout']}

STDERR:
{execution_result['stderr']}
"""

    repaired_code = call_gemini(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.0,
        output_format="text/plain",
    )

    validate_code(repaired_code)

    return repaired_code
