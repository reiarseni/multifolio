import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Facet
from app.schemas.story import StorySectionCreate, StorySectionUpdate
from app.services import story_service


@pytest.mark.asyncio
async def test_get_story_empty(db_session: AsyncSession):
    user_id = uuid.uuid4()
    facet = Facet(user_id=user_id, name="Test", slug="test-story-empty")
    db_session.add(facet)
    await db_session.commit()
    await db_session.refresh(facet)

    result = await story_service.get_story(db_session, user_id, facet.id)
    assert result == []


@pytest.mark.asyncio
async def test_upsert_section(db_session: AsyncSession):
    user_id = uuid.uuid4()
    facet = Facet(user_id=user_id, name="Test", slug="test-story-upsert")
    db_session.add(facet)
    await db_session.commit()
    await db_session.refresh(facet)

    data = StorySectionCreate(section_type="context", title="Test Section")
    section = await story_service.upsert_section(db_session, user_id, facet.id, data)
    assert section.section_type == "context"
    assert section.title == "Test Section"


@pytest.mark.asyncio
async def test_update_section(db_session: AsyncSession):
    user_id = uuid.uuid4()
    facet = Facet(user_id=user_id, name="Test", slug="test-story-update")
    db_session.add(facet)
    await db_session.commit()
    await db_session.refresh(facet)

    create_data = StorySectionCreate(section_type="context", title="Original")
    section = await story_service.upsert_section(db_session, user_id, facet.id, create_data)

    update_data = StorySectionUpdate(title="Updated")
    updated = await story_service.update_section(db_session, user_id, section.id, update_data)
    assert updated.title == "Updated"


@pytest.mark.asyncio
async def test_reorder_sections(db_session: AsyncSession):
    user_id = uuid.uuid4()
    facet = Facet(user_id=user_id, name="Test", slug="test-story-reorder")
    db_session.add(facet)
    await db_session.commit()
    await db_session.refresh(facet)

    data1 = StorySectionCreate(section_type="context", title="A", order=0)
    data2 = StorySectionCreate(section_type="process", title="B", order=1)
    section1 = await story_service.upsert_section(db_session, user_id, facet.id, data1)
    section2 = await story_service.upsert_section(db_session, user_id, facet.id, data2)

    result = await story_service.reorder_sections(
        db_session, user_id, facet.id, [section2.id, section1.id]
    )
    assert result[0].id == section2.id
    assert result[1].id == section1.id


@pytest.mark.asyncio
async def test_delete_section(db_session: AsyncSession):
    user_id = uuid.uuid4()
    facet = Facet(user_id=user_id, name="Test", slug="test-story-delete")
    db_session.add(facet)
    await db_session.commit()
    await db_session.refresh(facet)

    data = StorySectionCreate(section_type="context", title="To Delete")
    section = await story_service.upsert_section(db_session, user_id, facet.id, data)

    await story_service.delete_section(db_session, user_id, section.id)

    result = await story_service.get_story(db_session, user_id, facet.id)
    assert len(result) == 0


@pytest.mark.asyncio
async def test_update_section_not_found(db_session: AsyncSession):
    from fastapi import HTTPException

    user_id = uuid.uuid4()
    with pytest.raises(HTTPException) as exc_info:
        await story_service.update_section(
            db_session, user_id, uuid.uuid4(), StorySectionUpdate(title="X")
        )
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_section_not_found(db_session: AsyncSession):
    from fastapi import HTTPException

    user_id = uuid.uuid4()
    with pytest.raises(HTTPException) as exc_info:
        await story_service.delete_section(db_session, user_id, uuid.uuid4())
    assert exc_info.value.status_code == 404
