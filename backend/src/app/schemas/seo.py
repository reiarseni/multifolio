from pydantic import BaseModel


class SEOVariant(BaseModel):
    title: str
    description: str
    rationale: str


class SEOSuggestResponse(BaseModel):
    variants: list[SEOVariant]


class SEOUpdateRequest(BaseModel):
    meta_title: str | None = None
    meta_description: str | None = None


class SEOUpdateResponse(BaseModel):
    message: str


class SEOConfigResponse(BaseModel):
    meta_title: str | None
    meta_description: str | None
