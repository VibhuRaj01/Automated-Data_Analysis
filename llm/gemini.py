"""
gemini.py

Utility functions for interacting with Google's Gemini models.
"""

from __future__ import annotations
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API")

if API_KEY is None:
    raise EnvironmentError("GEMINI_API environment variable not found.")

client = genai.Client(api_key=API_KEY)


def call_gemini(
    *,
    system_prompt: str,
    user_prompt: str,
    model: str = "gemini-2.5-flash",
    temperature: float = 0.2,
    output_format: str = "text/plain",
) -> str:
    """
    Call a Gemini model and return the generated text.

    Parameters
    ----------
    system_prompt : str
        Instructions that define the model's behaviour.

    user_prompt : str
        The actual user/task prompt.

    model : str
        Gemini model name.

    temperature : float
        Sampling temperature.

    output_format : str
        The format of the output.

    Returns
    -------
    str
        Model response.
    """

    if not system_prompt.strip():
        raise ValueError("system_prompt cannot be empty.")

    if not user_prompt.strip():
        raise ValueError("user_prompt cannot be empty.")

    config = genai.types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=temperature,
        response_mime_type=output_format,
    )

    response = client.models.generate_content(
        model=model,
        contents=user_prompt,
        config=config,
    )

    if response.text is None:
        raise RuntimeError("Gemini returned an empty response.")

    # print(f"Gemini response: {response.text.strip()}")  # Debugging line
    return response.text.strip()
