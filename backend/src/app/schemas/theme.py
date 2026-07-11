import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ThemeResponse(BaseModel):
    id: uuid.UUID
    name: str
    tokens: dict
    is_public: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FacetThemeConfigResponse(BaseModel):
    theme_id: uuid.UUID
    theme: ThemeResponse
    theme_overrides: dict | None
    web_layout: str
    pdf_layout: str
    show_photo_web: bool
    show_photo_pdf: bool
    photo_shape: str
    section_order: list[str] | None = None

    model_config = {"from_attributes": True}


class FacetThemeConfigUpdate(BaseModel):
    theme_id: uuid.UUID | None = None
    theme_overrides: dict | None = None
    web_layout: str | None = None
    pdf_layout: str | None = None
    show_photo_web: bool | None = None
    show_photo_pdf: bool | None = None
    photo_shape: str | None = None
    section_order: list[str] | None = None


class ThemeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    tokens: dict = Field(..., max_length=10000)
    is_public: bool = False

    model_config = {"from_attributes": True}


class ThemeUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    tokens: dict | None = Field(None, max_length=10000)
    is_public: bool | None = None


class ThemeDelete(BaseModel):
    id: uuid.UUID
