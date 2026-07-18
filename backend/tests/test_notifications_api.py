import pytest
from httpx import AsyncClient

from app.schemas.notification import NotificationCreate
from app.services.notification_service import create_notification


def _headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


@pytest.mark.asyncio
async def test_list_notifications_empty(client: AsyncClient, auth_tokens):
    access_token, _ = auth_tokens
    resp = await client.get("/api/notifications", headers=_headers(access_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["unread_count"] == 0


@pytest.mark.asyncio
async def test_list_notifications_with_data(
    client: AsyncClient,
    auth_tokens,
    test_user,
    db_session,
):
    access_token, _ = auth_tokens

    for i in range(3):
        await create_notification(
            db_session,
            NotificationCreate(
                user_id=test_user["id"],
                type="notable_visit",
                title=f"Notif {i}",
                message=f"Message {i}",
            ),
        )

    resp = await client.get("/api/notifications", headers=_headers(access_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert data["unread_count"] == 3
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_list_notifications_unread_only(
    client: AsyncClient,
    auth_tokens,
    test_user,
    db_session,
):
    access_token, _ = auth_tokens

    n1 = await create_notification(
        db_session,
        NotificationCreate(
            user_id=test_user["id"],
            type="notable_visit",
            title="Read me",
            message="x",
        ),
    )

    await create_notification(
        db_session,
        NotificationCreate(
            user_id=test_user["id"],
            type="notable_visit",
            title="Unread",
            message="x",
        ),
    )

    await client.patch(
        f"/api/notifications/{n1.id}/read",
        headers=_headers(access_token),
    )

    resp = await client.get(
        "/api/notifications?unread_only=true",
        headers=_headers(access_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert data["unread_count"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Unread"


@pytest.mark.asyncio
async def test_mark_notification_read(
    client: AsyncClient,
    auth_tokens,
    test_user,
    db_session,
):
    access_token, _ = auth_tokens

    created = await create_notification(
        db_session,
        NotificationCreate(
            user_id=test_user["id"],
            type="notable_visit",
            title="Mark me",
            message="x",
        ),
    )

    resp = await client.patch(
        f"/api/notifications/{created.id}/read",
        headers=_headers(access_token),
    )
    assert resp.status_code == 200
    assert resp.json()["is_read"] is True


@pytest.mark.asyncio
async def test_mark_notification_read_not_found(
    client: AsyncClient,
    auth_tokens,
):
    access_token, _ = auth_tokens
    import uuid

    resp = await client.patch(
        f"/api/notifications/{uuid.uuid4()}/read",
        headers=_headers(access_token),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_mark_notification_read_unauthorized(client: AsyncClient):
    resp = await client.patch(
        "/api/notifications/some-id/read",
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_mark_all_read(
    client: AsyncClient,
    auth_tokens,
    test_user,
    db_session,
):
    access_token, _ = auth_tokens

    for i in range(3):
        await create_notification(
            db_session,
            NotificationCreate(
                user_id=test_user["id"],
                type="notable_visit",
                title=f"N{i}",
                message="x",
            ),
        )

    resp = await client.patch(
        "/api/notifications/read-all",
        headers=_headers(access_token),
    )
    assert resp.status_code == 200
    assert resp.json()["marked_read"] == 3

    get_resp = await client.get("/api/notifications", headers=_headers(access_token))
    assert get_resp.json()["unread_count"] == 0


@pytest.mark.asyncio
async def test_mark_all_read_unauthorized(client: AsyncClient):
    resp = await client.patch("/api/notifications/read-all")
    assert resp.status_code == 401
