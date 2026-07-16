import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Facet
from app.schemas.open_to_role import OpenToRoleUpdate
from app.services import open_to_role_service


@pytest.mark.asyncio
async def test_upsert_open_to_role_create(db_session: AsyncSession):
    user_id = uuid.uuid4()
    facet = Facet(user_id=user_id, name="Test", slug="test-otr")
    db_session.add(facet)
    await db_session.commit()
    await db_session.refresh(facet)

    data = OpenToRoleUpdate(status="available", role_type="backend")
    result = await open_to_role_service.upsert_open_to_role(db_session, user_id, facet.id, data)
    assert result.status == "available"
    assert result.role_type == "backend"


@pytest.mark.asyncio
async def test_upsert_open_to_role_update(db_session: AsyncSession):
    user_id = uuid.uuid4()
    facet = Facet(user_id=user_id, name="Test", slug="test-otr-update")
    db_session.add(facet)
    await db_session.commit()
    await db_session.refresh(facet)

    data = OpenToRoleUpdate(status="available")
    await open_to_role_service.upsert_open_to_role(db_session, user_id, facet.id, data)

    update_data = OpenToRoleUpdate(status="not_available")
    result = await open_to_role_service.upsert_open_to_role(
        db_session, user_id, facet.id, update_data
    )
    assert result.status == "not_available"


@pytest.mark.asyncio
async def test_get_open_to_role(db_session: AsyncSession):
    user_id = uuid.uuid4()
    facet = Facet(user_id=user_id, name="Test", slug="test-otr-get")
    db_session.add(facet)
    await db_session.commit()
    await db_session.refresh(facet)

    result = await open_to_role_service.get_open_to_role(db_session, user_id, facet.id)
    assert result is None

    data = OpenToRoleUpdate(status="available")
    await open_to_role_service.upsert_open_to_role(db_session, user_id, facet.id, data)

    result = await open_to_role_service.get_open_to_role(db_session, user_id, facet.id)
    assert result is not None
    assert result.status == "available"


@pytest.mark.asyncio
async def test_delete_open_to_role(db_session: AsyncSession):
    user_id = uuid.uuid4()
    facet = Facet(user_id=user_id, name="Test", slug="test-otr-delete")
    db_session.add(facet)
    await db_session.commit()
    await db_session.refresh(facet)

    data = OpenToRoleUpdate(status="available")
    await open_to_role_service.upsert_open_to_role(db_session, user_id, facet.id, data)

    await open_to_role_service.delete_open_to_role(db_session, user_id, facet.id)

    result = await open_to_role_service.get_open_to_role(db_session, user_id, facet.id)
    assert result is None


@pytest.mark.asyncio
async def test_delete_open_to_role_nonexistent(db_session: AsyncSession):
    user_id = uuid.uuid4()
    facet = Facet(user_id=user_id, name="Test", slug="test-otr-del-none")
    db_session.add(facet)
    await db_session.commit()
    await db_session.refresh(facet)

    await open_to_role_service.delete_open_to_role(db_session, user_id, facet.id)
