"""Tests for themes service functionality"""

import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import FacetThemeConfig, Theme
from app.schemas.theme import ThemeCreate
from app.services.themes import (
    create_theme,
    delete_theme,
    list_themes,
    publish_theme,
    unpublish_theme,
)


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
    assert "predefinido" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_list_themes_includes_own_private(db_session: AsyncSession):
    """Test that list_themes includes user's own private themes"""
    user_id = uuid.uuid4()

    theme_data = ThemeCreate(
        name="My Private Theme",
        tokens={"color": {"primary": "#000000"}},
        is_public=False,
    )

    await create_theme(db_session, user_id, theme_data)

    themes = await list_themes(db_session, user_id)
    assert any(t.name == "My Private Theme" for t in themes)


@pytest.mark.asyncio
async def test_list_themes_excludes_others_private(db_session: AsyncSession):
    """Test that list_themes excludes other users' private themes"""
    user_id1 = uuid.uuid4()
    user_id2 = uuid.uuid4()

    theme_data = ThemeCreate(
        name="Other Private Theme",
        tokens={"color": {"primary": "#000000"}},
        is_public=False,
    )

    await create_theme(db_session, user_id1, theme_data)

    themes = await list_themes(db_session, user_id2)
    assert not any(t.name == "Other Private Theme" for t in themes)


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

    theme = Theme(
        id=uuid.uuid4(),
        owner_id=user_id,
        name="minimal",
        tokens={"color": {"primary": "#ff0000"}},
        is_public=False,
    )
    db_session.add(theme)
    await db_session.commit()
    await db_session.refresh(theme)

    with pytest.raises(HTTPException) as exc_info:
        await delete_theme(db_session, user_id, theme.id)

    assert exc_info.value.status_code == 422
    assert "No se pueden eliminar los temas predefinidos del sistema" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_delete_theme_in_use_forbidden(db_session: AsyncSession):
    """Test that deleting a theme in use by a facet is forbidden"""
    user_id = uuid.uuid4()

    theme_data = ThemeCreate(
        name="Used Theme",
        tokens={"color": {"primary": "#ff0000"}},
        is_public=False,
    )

    theme = await create_theme(db_session, user_id, theme_data)

    facet_config = FacetThemeConfig(
        facet_id=uuid.uuid4(),
        theme_id=theme.id,
        theme_overrides=None,
        web_layout="single-column",
        pdf_layout="classic",
        show_photo_web=True,
        show_photo_pdf=True,
        photo_shape="circle",
    )
    db_session.add(facet_config)
    await db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await delete_theme(db_session, user_id, theme.id)

    assert exc_info.value.status_code == 409
    assert "está siendo usado por una faceta" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_publish_theme_success(db_session: AsyncSession):
    """Test successful theme publication"""
    user_id = uuid.uuid4()

    theme_data = ThemeCreate(
        name="Publishable Theme",
        tokens={
            "color": {
                "primary": "#1a1a1a",
                "background": "#ffffff",
                "text_heading": "#1a1a1a",
                "text_body": "#333333",
                "text_muted": "#666666",
                "accent": "#0066cc",
                "surface": "#f5f5f5",
                "border": "#e0e0e0",
            }
        },
        is_public=False,
    )

    theme = await create_theme(db_session, user_id, theme_data)
    published = await publish_theme(db_session, user_id, theme.id)

    assert published.is_public is True


@pytest.mark.asyncio
async def test_publish_theme_wcag_fails(db_session: AsyncSession):
    """Test that publish rejects themes failing WCAG"""
    user_id = uuid.uuid4()

    theme_data = ThemeCreate(
        name="Bad Contrast Theme",
        tokens={
            "color": {
                "primary": "#ffffff",
                "background": "#ffffff",
                "text_heading": "#ffffff",
                "text_body": "#ffffff",
                "text_muted": "#ffffff",
                "accent": "#ffffff",
                "surface": "#ffffff",
                "border": "#ffffff",
            }
        },
        is_public=False,
    )

    theme = await create_theme(db_session, user_id, theme_data)

    with pytest.raises(HTTPException) as exc_info:
        await publish_theme(db_session, user_id, theme.id)

    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_publish_theme_external_assets_fails(db_session: AsyncSession):
    """Test that publish rejects themes with external assets"""
    user_id = uuid.uuid4()

    theme_data = ThemeCreate(
        name="External Asset Theme",
        tokens={
            "color": {
                "primary": "#1a1a1a",
                "background": "#ffffff",
                "text_heading": "#1a1a1a",
                "text_body": "#333333",
                "text_muted": "#666666",
                "accent": "url(https://example.com/font.woff)",
                "surface": "#f5f5f5",
                "border": "#e0e0e0",
            }
        },
        is_public=False,
    )

    theme = await create_theme(db_session, user_id, theme_data)

    with pytest.raises(HTTPException) as exc_info:
        await publish_theme(db_session, user_id, theme.id)

    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_publish_theme_not_owner(db_session: AsyncSession):
    """Test that publishing another user's theme is forbidden"""
    user_id1 = uuid.uuid4()
    user_id2 = uuid.uuid4()

    theme_data = ThemeCreate(
        name="My Theme",
        tokens={
            "color": {
                "primary": "#1a1a1a",
                "background": "#ffffff",
                "text_heading": "#1a1a1a",
                "text_body": "#333333",
                "text_muted": "#666666",
                "accent": "#0066cc",
                "surface": "#f5f5f5",
                "border": "#e0e0e0",
            }
        },
        is_public=False,
    )

    theme = await create_theme(db_session, user_id1, theme_data)

    with pytest.raises(HTTPException) as exc_info:
        await publish_theme(db_session, user_id2, theme.id)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_unpublish_theme_success(db_session: AsyncSession):
    """Test successful theme unpublish"""
    user_id = uuid.uuid4()

    theme_data = ThemeCreate(
        name="Published Theme",
        tokens={
            "color": {
                "primary": "#1a1a1a",
                "background": "#ffffff",
                "text_heading": "#1a1a1a",
                "text_body": "#333333",
                "text_muted": "#666666",
                "accent": "#0066cc",
                "surface": "#f5f5f5",
                "border": "#e0e0e0",
            }
        },
        is_public=True,
    )

    theme = await create_theme(db_session, user_id, theme_data)
    unpublished = await unpublish_theme(db_session, user_id, theme.id)

    assert unpublished.is_public is False
