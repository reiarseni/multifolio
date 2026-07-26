from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.review_link_service import (
    create_link,
    deactivate_link,
    list_links,
    validate_link,
)


@pytest.mark.asyncio
async def test_create_link(db_session):
    with patch("app.services.review_link_service.select") as mock_select:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock(id=uuid.uuid4())
        mock_select.return_value.where.return_value = mock_select
        mock_select.return_value = mock_result
        db_session.execute = AsyncMock(return_value=mock_result)
        db_session.add = MagicMock()
        db_session.commit = AsyncMock()
        db_session.refresh = AsyncMock()

        link = await create_link(db_session, uuid.uuid4(), uuid.uuid4())
        assert link is not None
        db_session.add.assert_called_once()


@pytest.mark.asyncio
async def test_validate_link(db_session):
    with patch("app.services.review_link_service.select") as mock_select:
        mock_link = MagicMock()
        mock_link.token = "token123"
        mock_link.is_active = True

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_link
        mock_select.return_value.where.return_value = mock_select
        mock_select.return_value = mock_result
        db_session.execute = AsyncMock(return_value=mock_result)

        result = await validate_link(db_session, "token123")
        assert result == mock_link


@pytest.mark.asyncio
async def test_validate_link_not_found(db_session):
    with patch("app.services.review_link_service.select") as mock_select:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_select.return_value.where.return_value = mock_select
        mock_select.return_value = mock_result
        db_session.execute = AsyncMock(return_value=mock_result)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await validate_link(db_session, "nonexistent")
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_deactivate_link(db_session):
    user_id = uuid.uuid4()
    link_id = uuid.uuid4()

    with patch("app.services.review_link_service.select") as mock_select:
        mock_link = MagicMock()
        mock_link.id = link_id
        mock_link.created_by = user_id
        mock_link.is_active = True

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_link
        mock_select.return_value.where.return_value = mock_select
        mock_select.return_value = mock_result
        db_session.execute = AsyncMock(return_value=mock_result)
        db_session.commit = AsyncMock()

        await deactivate_link(db_session, user_id, link_id)
        assert mock_link.is_active is False


@pytest.mark.asyncio
async def test_deactivate_link_not_found(db_session):
    with patch("app.services.review_link_service.select") as mock_select:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_select.return_value.where.return_value = mock_select
        mock_select.return_value = mock_result
        db_session.execute = AsyncMock(return_value=mock_result)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await deactivate_link(db_session, uuid.uuid4(), uuid.uuid4())
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_deactivate_link_wrong_owner(db_session):
    with patch("app.services.review_link_service.select") as mock_select:
        mock_link = MagicMock()
        mock_link.created_by = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_link
        mock_select.return_value.where.return_value = mock_select
        mock_select.return_value = mock_result
        db_session.execute = AsyncMock(return_value=mock_result)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await deactivate_link(db_session, uuid.uuid4(), uuid.uuid4())
        assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_list_links(db_session):
    with patch("app.services.review_link_service.select") as mock_select:
        mock_facet = MagicMock()
        mock_facet_result = MagicMock()
        mock_facet_result.scalar_one_or_none.return_value = mock_facet

        mock_links = [MagicMock(), MagicMock()]
        mock_links_result = MagicMock()
        mock_links_result.scalars.return_value.all.return_value = mock_links

        mock_select.return_value.where.return_value = mock_select
        mock_select.return_value.order_by.return_value = mock_select
        db_session.execute = AsyncMock(side_effect=[mock_facet_result, mock_links_result])

        result = await list_links(db_session, uuid.uuid4(), uuid.uuid4())
        assert len(result) == 2


@pytest.mark.asyncio
async def test_list_links_facet_not_found(db_session):
    with patch("app.services.review_link_service.select") as mock_select:
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_select.return_value.where.return_value = mock_select
        mock_select.return_value = mock_result
        db_session.execute = AsyncMock(return_value=mock_result)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await list_links(db_session, uuid.uuid4(), uuid.uuid4())
        assert exc_info.value.status_code == 404
