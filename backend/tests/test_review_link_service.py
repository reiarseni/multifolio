from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.review_link_service import (
    _hash_password,
    _verify_password,
    access_link,
    create_link,
    delete_link,
    list_links,
    validate_link,
)


def test_hash_password():
    hashed = _hash_password("test123")
    assert _verify_password("test123", hashed)
    assert not _verify_password("wrong", hashed)


@pytest.mark.asyncio
async def test_create_link(db_session):
    with patch("app.services.review_link_service.select") as mock_select:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock(id=uuid.uuid4())
        mock_select.return_value.where.return_value = mock_select
        mock_select.return_value = mock_result
        db_session.execute = AsyncMock(return_value=mock_result)

        from app.schemas.review_link import ReviewLinkCreate

        data = ReviewLinkCreate(label="Test Link")
        link = await create_link(db_session, uuid.uuid4(), uuid.uuid4(), data)
        assert link.label == "Test Link"


@pytest.mark.asyncio
async def test_list_links(db_session):
    with patch("app.services.review_link_service.select") as _:
        mock_facet = MagicMock()
        mock_facet_result = MagicMock()
        mock_facet_result.scalar_one_or_none.return_value = mock_facet

        mock_links = [MagicMock(label="Link 1"), MagicMock(label="Link 2")]
        mock_links_result = MagicMock()
        mock_links_result.scalars.return_value.all.return_value = mock_links

        db_session.execute = AsyncMock(side_effect=[mock_facet_result, mock_links_result])

        result = await list_links(db_session, uuid.uuid4(), uuid.uuid4())
        assert len(result) == 2


@pytest.mark.asyncio
async def test_delete_link(db_session):
    with patch("app.services.review_link_service.select") as _:
        mock_link = MagicMock()
        mock_link.facet_id = uuid.uuid4()
        mock_link_result = MagicMock()
        mock_link_result.scalar_one_or_none.return_value = mock_link

        mock_facet = MagicMock()
        mock_facet_result = MagicMock()
        mock_facet_result.scalar_one_or_none.return_value = mock_facet

        db_session.execute = AsyncMock(side_effect=[mock_link_result, mock_facet_result])
        db_session.delete = AsyncMock()
        db_session.commit = AsyncMock()

        await delete_link(db_session, uuid.uuid4(), uuid.uuid4())
        db_session.delete.assert_called_once()


@pytest.mark.asyncio
async def test_validate_link(db_session):
    link_id = uuid.uuid4()
    facet_id = uuid.uuid4()

    with patch("app.services.review_link_service.select") as mock_select:
        mock_link = MagicMock()
        mock_link.id = link_id
        mock_link.facet_id = facet_id
        mock_link.expires_at = None
        mock_link.single_use = False
        mock_link.requires_password = False

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_link
        mock_select.return_value.where.return_value = mock_select
        mock_select.return_value = mock_result
        db_session.execute = AsyncMock(return_value=mock_result)

        valid, fid = await validate_link(db_session, "token123", None)
        assert valid is True
        assert fid == facet_id


@pytest.mark.asyncio
async def test_validate_link_expired(db_session):
    with patch("app.services.review_link_service.select") as mock_select:
        mock_link = MagicMock()
        mock_link.expires_at = datetime.now(UTC) - timedelta(hours=1)
        mock_link.requires_password = False

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_link
        mock_select.return_value.where.return_value = mock_select
        mock_select.return_value = mock_result
        db_session.execute = AsyncMock(return_value=mock_result)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await validate_link(db_session, "token123", None)
        assert exc_info.value.status_code == 410


@pytest.mark.asyncio
async def test_validate_link_password_required(db_session):
    with patch("app.services.review_link_service.select") as mock_select:
        mock_link = MagicMock()
        mock_link.expires_at = None
        mock_link.single_use = False
        mock_link.requires_password = True
        mock_link.password_hash = _hash_password("correct")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_link
        mock_select.return_value.where.return_value = mock_select
        mock_select.return_value = mock_result
        db_session.execute = AsyncMock(return_value=mock_result)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await validate_link(db_session, "token123", None)
        assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_validate_link_wrong_password(db_session):
    with patch("app.services.review_link_service.select") as mock_select:
        mock_link = MagicMock()
        mock_link.expires_at = None
        mock_link.single_use = False
        mock_link.requires_password = True
        mock_link.password_hash = _hash_password("correct")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_link
        mock_select.return_value.where.return_value = mock_select
        mock_select.return_value = mock_result
        db_session.execute = AsyncMock(return_value=mock_result)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await validate_link(db_session, "token123", "wrong")
        assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_validate_link_single_use(db_session):
    with patch("app.services.review_link_service.select") as mock_select:
        mock_link = MagicMock()
        mock_link.expires_at = None
        mock_link.single_use = True
        mock_link.is_used = True
        mock_link.requires_password = False

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_link
        mock_select.return_value.where.return_value = mock_select
        mock_select.return_value = mock_result
        db_session.execute = AsyncMock(return_value=mock_result)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await validate_link(db_session, "token123", None)
        assert exc_info.value.status_code == 410


@pytest.mark.asyncio
async def test_access_link(db_session):
    with patch("app.services.review_link_service.select") as mock_select:
        mock_link = MagicMock()
        mock_link.expires_at = None
        mock_link.single_use = False
        mock_link.is_used = False

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_link
        mock_select.return_value.where.return_value = mock_select
        mock_select.return_value = mock_result
        db_session.execute = AsyncMock(return_value=mock_result)

        result = await access_link(db_session, "token123")
        assert result == mock_link


@pytest.mark.asyncio
async def test_access_link_not_found(db_session):
    with patch("app.services.review_link_service.select") as mock_select:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_select.return_value.where.return_value = mock_select
        mock_select.return_value = mock_result
        db_session.execute = AsyncMock(return_value=mock_result)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await access_link(db_session, "nonexistent")
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_access_link_expired(db_session):
    with patch("app.services.review_link_service.select") as mock_select:
        mock_link = MagicMock()
        mock_link.expires_at = datetime.now(UTC) - timedelta(hours=1)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_link
        mock_select.return_value.where.return_value = mock_select
        mock_select.return_value = mock_result
        db_session.execute = AsyncMock(return_value=mock_result)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await access_link(db_session, "token123")
        assert exc_info.value.status_code == 410
