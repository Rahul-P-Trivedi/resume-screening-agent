"""
STEP 2 & 3: talks to the LLM (Claude) using the system prompt defined in
config.py, and parses its structured JSON response.
"""

import json
import re

import anthropic

from src.config import ANTHROPIC_API_KEY, CLAUDE_MODEL, SYSTEM_PROMPT

_client = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        if not ANTHROPIC_API_KEY:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key."
            )
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def _extract_json(raw_text: str) -> dict:
    """Claude is instructed to return pure JSON, but this strips markdown
    fences defensively in case the model wraps it anyway."""
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```json\s*|^```\s*|```$", "", cleaned, flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def screen_resume(job_description: str, resume_text: str, filename: str) -> dict:
    """
    Sends one resume + the JD to Claude and returns the parsed structured
    assessment. Raises on API or parsing failure (caller should catch).
    """
    client = get_client()

    user_message = f"""JOB DESCRIPTION:
{job_description}

---

CANDIDATE RESUME ({filename}):
{resume_text}

---

Evaluate this candidate against the job description and return the JSON object as instructed."""

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_text = "".join(
        block.text for block in response.content if getattr(block, "type", "") == "text"
    )

    try:
        return _extract_json(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse LLM response as JSON for {filename}: {e}\nRaw: {raw_text[:300]}")
