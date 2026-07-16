from __future__ import annotations

import json
import logging

from openai import AsyncOpenAI

from app.core.config import get_settings
from app.prompts.storytelling import (
    SYSTEM_PROMPT,
    apply_suggestion_prompt,
    expand_section_prompt,
    improve_section_prompt,
    suggest_headline_prompt,
)

logger = logging.getLogger(__name__)

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        settings = get_settings()
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def _chat(user_message: str, *, temperature: float = 0.7) -> str:
    client = _get_client()
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=temperature,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content or ""


async def improve_content(content: str, section_type: str, title: str) -> str:
    prompt = improve_section_prompt(section_type, title, content)
    return await _chat(prompt)


async def expand_section(content: str, section_type: str, title: str) -> str:
    prompt = expand_section_prompt(section_type, title, content)
    return await _chat(prompt, temperature=0.8)


async def suggest_headline(title: str, bio: str, target_role: str) -> dict[str, str]:
    prompt = suggest_headline_prompt(title, bio, target_role)
    raw = await _chat(prompt, temperature=0.9)
    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(cleaned)
    except (json.JSONDecodeError, IndexError):
        logger.warning("Failed to parse headline suggestion, returning defaults")
        return {"title": title, "bio": bio}


async def apply_suggestion(original: str, suggestion: str) -> str:
    prompt = apply_suggestion_prompt(original, suggestion)
    return await _chat(prompt, temperature=0.3)
