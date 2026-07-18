import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.notification import NotificationCreate
from app.services.notification_service import (
    create_notification,
    get_user_notifications,
    mark_all_as_read,
    mark_as_read,
)


@pytest.mark.asyncio
async def test_create_notification(db_session: AsyncSession):
    user_id = uuid.uuid4()
    data = NotificationCreate(
        user_id=user_id,
        type="notable_visit",
        title="Test title",
        message="Test message",
        referrer_domain="github.com",
        extra_data={"domain": "github.com", "category": "professional_network"},
    )
    result = await create_notification(db_session, data)

    assert result.id is not None
    assert result.user_id == user_id
    assert result.type == "notable_visit"
    assert result.title == "Test title"
    assert result.message == "Test message"
    assert result.referrer_domain == "github.com"
    assert result.is_read is False
    assert result.extra_data == {"domain": "github.com", "category": "professional_network"}
    assert result.created_at is not None


@pytest.mark.asyncio
async def test_create_notification_with_facet(db_session: AsyncSession):
    user_id = uuid.uuid4()
    facet_id = uuid.uuid4()
    data = NotificationCreate(
        user_id=user_id,
        facet_id=facet_id,
        type="notable_visit",
        title="Visit from example.com",
        message="Your facet received a visit.",
    )
    result = await create_notification(db_session, data)

    assert result.facet_id == facet_id
    assert result.referrer_domain is None


@pytest.mark.asyncio
async def test_get_user_notifications_empty(db_session: AsyncSession):
    user_id = uuid.uuid4()
    result = await get_user_notifications(db_session, user_id)

    assert result.items == []
    assert result.total == 0
    assert result.unread_count == 0


@pytest.mark.asyncio
async def test_get_user_notifications_with_data(db_session: AsyncSession):
    user_id = uuid.uuid4()
    other_user_id = uuid.uuid4()

    for i in range(3):
        data = NotificationCreate(
            user_id=user_id,
            type="notable_visit",
            title=f"Notification {i}",
            message=f"Message {i}",
        )
        await create_notification(db_session, data)

    data = NotificationCreate(
        user_id=other_user_id,
        type="notable_visit",
        title="Other user",
        message="Should not appear",
    )
    await create_notification(db_session, data)

    result = await get_user_notifications(db_session, user_id)

    assert result.total == 3
    assert len(result.items) == 3
    assert result.unread_count == 3
    assert all(n.title.startswith("Notification") for n in result.items)


@pytest.mark.asyncio
async def test_get_user_notifications_unread_only(db_session: AsyncSession):
    user_id = uuid.uuid4()

    n1 = await create_notification(
        db_session,
        NotificationCreate(user_id=user_id, type="test", title="Unread", message="x"),
    )
    await create_notification(
        db_session,
        NotificationCreate(user_id=user_id, type="test", title="Also unread", message="x"),
    )

    await mark_as_read(db_session, n1.id, user_id)

    result = await get_user_notifications(db_session, user_id, unread_only=True)

    assert result.total == 2
    assert result.unread_count == 1
    assert len(result.items) == 1
    assert result.items[0].title == "Also unread"


@pytest.mark.asyncio
async def test_mark_as_read(db_session: AsyncSession):
    user_id = uuid.uuid4()

    created = await create_notification(
        db_session,
        NotificationCreate(user_id=user_id, type="test", title="Mark me", message="x"),
    )

    result = await mark_as_read(db_session, created.id, user_id)

    assert result is not None
    assert result.is_read is True


@pytest.mark.asyncio
async def test_mark_as_read_wrong_user(db_session: AsyncSession):
    user_id = uuid.uuid4()
    wrong_user = uuid.uuid4()

    created = await create_notification(
        db_session,
        NotificationCreate(user_id=user_id, type="test", title="Not yours", message="x"),
    )

    result = await mark_as_read(db_session, created.id, wrong_user)

    assert result is None


@pytest.mark.asyncio
async def test_mark_as_read_not_found(db_session: AsyncSession):
    result = await mark_as_read(db_session, uuid.uuid4(), uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_mark_all_as_read(db_session: AsyncSession):
    user_id = uuid.uuid4()

    for i in range(5):
        await create_notification(
            db_session,
            NotificationCreate(user_id=user_id, type="test", title=f"N{i}", message="x"),
        )

    count = await mark_all_as_read(db_session, user_id)

    assert count == 5

    result = await get_user_notifications(db_session, user_id)
    assert result.unread_count == 0
    assert all(n.is_read for n in result.items)


@pytest.mark.asyncio
async def test_mark_all_as_read_no_notifications(db_session: AsyncSession):
    count = await mark_all_as_read(db_session, uuid.uuid4())
    assert count == 0


@pytest.mark.asyncio
async def test_get_user_notifications_pagination(db_session: AsyncSession):
    user_id = uuid.uuid4()

    for i in range(25):
        await create_notification(
            db_session,
            NotificationCreate(user_id=user_id, type="test", title=f"N{i}", message="x"),
        )

    page_1 = await get_user_notifications(db_session, user_id, limit=10, offset=0)
    assert len(page_1.items) == 10
    assert page_1.total == 25

    page_2 = await get_user_notifications(db_session, user_id, limit=10, offset=10)
    assert len(page_2.items) == 10

    page_3 = await get_user_notifications(db_session, user_id, limit=10, offset=20)
    assert len(page_3.items) == 5
