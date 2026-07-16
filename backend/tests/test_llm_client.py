from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.llm_client import (
    _chat,
    _get_client,
    apply_suggestion,
    expand_section,
    improve_content,
    suggest_headline,
)
from app.prompts.storytelling import (
    SYSTEM_PROMPT,
    apply_suggestion_prompt,
    expand_section_prompt,
    improve_section_prompt,
    suggest_headline_prompt,
)


def test_improve_section_prompt():
    prompt = improve_section_prompt("proceso", "Mi Proyecto", "Hice un proyecto")
    assert "proceso" in prompt
    assert "Mi Proyecto" in prompt
    assert "Hice un proyecto" in prompt
    assert "verbos de acción" in prompt


def test_expand_section_prompt():
    prompt = expand_section_prompt("impact", "Impacto", "Tuve impacto")
    assert "impact" in prompt
    assert "Impacto" in prompt
    assert "narrativamente" in prompt


def test_expand_section_prompt_with_process():
    prompt = expand_section_prompt("proceso", "Proceso", "Descripción")
    assert "Proceso → Solución → Impacto" in prompt


def test_suggest_headline_prompt():
    prompt = suggest_headline_prompt("Dev", "Bio here", "Senior Developer")
    assert "Dev" in prompt
    assert "Bio here" in prompt
    assert "Senior Developer" in prompt
    assert "JSON" in prompt


def test_apply_suggestion_prompt():
    prompt = apply_suggestion_prompt("Original", "Suggestion")
    assert "Original" in prompt
    assert "Suggestion" in prompt


def test_system_prompt():
    assert "portfolio" in SYSTEM_PROMPT
    assert "profesional" in SYSTEM_PROMPT


@pytest.mark.asyncio
async def test_chat():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Improved text"))]

    with patch("app.core.llm_client._get_client") as mock_get:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_get.return_value = mock_client

        result = await _chat("test prompt")
        assert result == "Improved text"


@pytest.mark.asyncio
async def test_improve_content():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Better content"))]

    with patch("app.core.llm_client._get_client") as mock_get:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_get.return_value = mock_client

        result = await improve_content("content", "proceso", "title")
        assert result == "Better content"


@pytest.mark.asyncio
async def test_expand_section():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Expanded content"))]

    with patch("app.core.llm_client._get_client") as mock_get:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_get.return_value = mock_client

        result = await expand_section("content", "proceso", "title")
        assert result == "Expanded content"


@pytest.mark.asyncio
async def test_suggest_headline():
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=json.dumps({"title": "New Title", "bio": "New Bio"})))
    ]

    with patch("app.core.llm_client._get_client") as mock_get:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_get.return_value = mock_client

        result = await suggest_headline("Old Title", "Old Bio", "Developer")
        assert result["title"] == "New Title"
        assert result["bio"] == "New Bio"


@pytest.mark.asyncio
async def test_suggest_headline_invalid_json():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Not JSON"))]

    with patch("app.core.llm_client._get_client") as mock_get:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_get.return_value = mock_client

        result = await suggest_headline("Old Title", "Old Bio", "Developer")
        assert result["title"] == "Old Title"
        assert result["bio"] == "Old Bio"


@pytest.mark.asyncio
async def test_apply_suggestion():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Applied suggestion"))]

    with patch("app.core.llm_client._get_client") as mock_get:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_get.return_value = mock_client

        result = await apply_suggestion("original", "suggestion")
        assert result == "Applied suggestion"


def test_get_client():
    with patch("app.core.llm_client.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(openai_api_key="test-key")
        client = _get_client()
        assert client is not None
