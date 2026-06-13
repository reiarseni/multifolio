"""Tests for themes service functionality"""

import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Theme
from app.schemas.theme import ThemeCreate
from app.services.themes import create_theme, delete_theme


@pytest.mark.asyncio
async def test_create_theme_success(db_session: AsyncSession):
    """Test successful theme creation"""
    user_id = uuid.uuid4()

    theme_data = ThemeCreate(
        name="Test Theme",
        tokens={"color": {"primary": "#ff0000"}},
        is_public=False,
    )

    theme = await create_theme(db_session, user_id, theme_data)

    assert theme.id is not None
    assert theme.name == "Test Theme"
    assert theme.owner_id == user_id
    assert theme.is_public is False
    assert theme.tokens == {"color": {"primary": "#ff0000"}}


@pytest.mark.asyncio
async def test_create_theme_predefined_name_forbidden(db_session: AsyncSession):
    """Test that creating a theme with predefined name is forbidden"""
    user_id = uuid.uuid4()

    theme_data = ThemeCreate(
        name="minimal",
        tokens={"color": {"primary": "#ff0000"}},
        is_public=False,
    )

    with pytest.raises(HTTPException) as exc_info:
        await create_theme(db_session, user_id, theme_data)

    assert exc_info.value.status_code == 422
    assert "No se puede crear un tema con el nombre" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_delete_theme_success(db_session: AsyncSession):
    """Test successful theme deletion"""
    user_id = uuid.uuid4()

    theme_data = ThemeCreate(
        name="Test Theme",
        tokens={"color": {"primary": "#ff0000"}},
        is_public=False,
    )

    theme = await create_theme(db_session, user_id, theme_data)

    deleted_theme = await delete_theme(db_session, user_id, theme.id)

    assert deleted_theme.id == theme.id


@pytest.mark.asyncio
async def test_delete_theme_not_owner(db_session: AsyncSession):
    """Test that deleting another user's theme is forbidden"""
    user_id1 = uuid.uuid4()
    user_id2 = uuid.uuid4()

    theme_data = ThemeCreate(
        name="Test Theme",
        tokens={"color": {"primary": "#ff0000"}},
        is_public=False,
    )

    theme = await create_theme(db_session, user_id1, theme_data)

    with pytest.raises(HTTPException) as exc_info:
        await delete_theme(db_session, user_id2, theme.id)

    assert exc_info.value.status_code == 403
    assert "No tiene permiso para eliminar este tema" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_delete_theme_predefined_name_forbidden(db_session: AsyncSession):
    """Test that deleting predefined themes is forbidden"""
    user_id = uuid.uuid4()

    theme_data = ThemeCreate(
        name="minimal",
        tokens={"color": {"primary": "#ff0000"}},
        is_public=False,
    )

    theme = await create_theme(db_session, user_id, theme_data)

    with pytest.raises(HTTPException) as exc_info:
        await delete_theme(db_session, user_id, theme.id)

    assert exc_info.value.status_code == 422
    assert "No se pueden eliminar los temas predefinidos del sistema" in str(exc_info.value.detail)
