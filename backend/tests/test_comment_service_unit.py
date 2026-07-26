"""Direct unit tests for comment_service.py and review_link_service.py."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.profile import Facet
from app.models.review_link import ReviewLink
from app.schemas.comment import CommentCreate
from app.services import comment_service, review_link_service


@pytest.mark.asyncio
async def test_get_facet_by_link_valid(db_session: AsyncSession, auth_tokens):
    """Direct test of _get_facet_by_link with valid link and facet."""
    from app.core.security import decode_token

    access_token, _ = auth_tokens
    payload = decode_token(access_token)
    user_id = uuid.UUID(payload["sub"])

    facet = Facet(user_id=user_id, name="Direct Test", slug="direct-test")
    db_session.add(facet)
    await db_session.flush()

    link = ReviewLink(facet_id=facet.id, created_by=user_id, token="test-token-123", is_active=True)
    db_session.add(link)
    await db_session.commit()

    result = await comment_service._get_facet_by_link(db_session, "test-token-123")
    assert result.id == facet.id


@pytest.mark.asyncio
async def test_get_facet_by_link_invalid(db_session: AsyncSession):
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await comment_service._get_facet_by_link(db_session, "nonexistent")
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_create_comment_by_token_unit(db_session: AsyncSession, auth_tokens):
    from app.core.security import decode_token

    access_token, _ = auth_tokens
    payload = decode_token(access_token)
    user_id = uuid.UUID(payload["sub"])

    facet = Facet(user_id=user_id, name="Unit Test", slug="unit-test")
    db_session.add(facet)
    await db_session.flush()

    link = ReviewLink(facet_id=facet.id, created_by=user_id, token="unit-token", is_active=True)
    db_session.add(link)
    await db_session.commit()

    data = CommentCreate(content="Test from unit test")
    comment = await comment_service.create_comment_by_token(db_session, "unit-token", data)
    assert comment.content == "Test from unit test"
    assert comment.facet_id == facet.id


@pytest.mark.asyncio
async def test_get_comments_by_token_unit(db_session: AsyncSession, auth_tokens):
    from app.core.security import decode_token

    access_token, _ = auth_tokens
    payload = decode_token(access_token)
    user_id = uuid.UUID(payload["sub"])

    facet = Facet(user_id=user_id, name="Get Test", slug="get-test")
    db_session.add(facet)
    await db_session.flush()

    link = ReviewLink(facet_id=facet.id, created_by=user_id, token="get-token", is_active=True)
    db_session.add(link)
    await db_session.commit()

    c = Comment(facet_id=facet.id, content="Hello")
    db_session.add(c)
    await db_session.commit()

    comments = await comment_service.get_comments_by_token(db_session, "get-token")
    assert len(comments) == 1
    assert comments[0].content == "Hello"


@pytest.mark.asyncio
async def test_get_comments_by_facet_id_unit(db_session: AsyncSession, auth_tokens):
    from app.core.security import decode_token

    access_token, _ = auth_tokens
    payload = decode_token(access_token)
    user_id = uuid.UUID(payload["sub"])

    facet = Facet(user_id=user_id, name="Facet ID Test", slug="facet-id-test")
    db_session.add(facet)
    await db_session.commit()

    c = Comment(facet_id=facet.id, content="By Facet ID")
    db_session.add(c)
    await db_session.commit()

    comments = await comment_service.get_comments_by_facet_id(db_session, facet.id)
    assert len(comments) == 1
    assert comments[0].content == "By Facet ID"


@pytest.mark.asyncio
async def test_resolve_comment_unit(db_session: AsyncSession, auth_tokens):
    from app.core.security import decode_token

    access_token, _ = auth_tokens
    payload = decode_token(access_token)
    user_id = uuid.UUID(payload["sub"])

    facet = Facet(user_id=user_id, name="Resolve Test", slug="resolve-test")
    db_session.add(facet)
    await db_session.flush()

    c = Comment(facet_id=facet.id, content="To resolve")
    db_session.add(c)
    await db_session.commit()

    resolved = await comment_service.resolve_comment(db_session, user_id, c.id)
    assert resolved.status == "resolved"


@pytest.mark.asyncio
async def test_resolve_comment_not_found_unit(db_session: AsyncSession, auth_tokens):
    from fastapi import HTTPException

    from app.core.security import decode_token

    access_token, _ = auth_tokens
    payload = decode_token(access_token)
    user_id = uuid.UUID(payload["sub"])

    with pytest.raises(HTTPException) as exc:
        await comment_service.resolve_comment(db_session, user_id, uuid.uuid4())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_unread_count_unit(db_session: AsyncSession, auth_tokens):
    from app.core.security import decode_token

    access_token, _ = auth_tokens
    payload = decode_token(access_token)
    user_id = uuid.UUID(payload["sub"])

    facet = Facet(user_id=user_id, name="Unread Test", slug="unread-test")
    db_session.add(facet)
    await db_session.flush()

    c = Comment(facet_id=facet.id, content="Pending comment", status="pending")
    db_session.add(c)
    await db_session.commit()

    count = await comment_service.get_unread_count(db_session, user_id)
    assert count >= 1


@pytest.mark.asyncio
async def test_create_link_unit(db_session: AsyncSession, auth_tokens):
    from fastapi import HTTPException

    from app.core.security import decode_token

    access_token, _ = auth_tokens
    payload = decode_token(access_token)
    user_id = uuid.UUID(payload["sub"])

    with pytest.raises(HTTPException) as exc:
        await review_link_service.create_link(db_session, user_id, uuid.uuid4())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_validate_link_unit(db_session: AsyncSession):
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await review_link_service.validate_link(db_session, "invalid-token")
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_deactivate_link_not_found_unit(db_session: AsyncSession, auth_tokens):
    from fastapi import HTTPException

    from app.core.security import decode_token

    access_token, _ = auth_tokens
    payload = decode_token(access_token)
    user_id = uuid.UUID(payload["sub"])

    with pytest.raises(HTTPException) as exc:
        await review_link_service.deactivate_link(db_session, user_id, uuid.uuid4())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_list_links_not_found_unit(db_session: AsyncSession, auth_tokens):
    from fastapi import HTTPException

    from app.core.security import decode_token

    access_token, _ = auth_tokens
    payload = decode_token(access_token)
    user_id = uuid.UUID(payload["sub"])

    with pytest.raises(HTTPException) as exc:
        await review_link_service.list_links(db_session, user_id, uuid.uuid4())
    assert exc.value.status_code == 404
