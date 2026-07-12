from pydantic import BaseModel, Field, field_validator


class DigestPreviewItem(BaseModel):
    source: str
    title: str
    url: str
    score: int | None = None


class DigestPreviewRequest(BaseModel):
    sources: dict[str, bool] = Field(
        default_factory=lambda: {
            "hn": True,
            "techcrunch": True,
            "arxiv": True,
            "tip": True,
        },
        description="Map of content sources to include or exclude.",
    )
    limits: dict[str, int] | None = Field(
        default=None,
        description="Optional per-source item limits between 1 and 20.",
    )

    @field_validator("sources")
    @classmethod
    def validate_sources(cls, value):
        known = {"hn", "techcrunch", "arxiv", "tip"}
        unknown = set(value.keys()) - known
        if unknown:
            raise ValueError(f"Unknown sources: {', '.join(sorted(unknown))}")
        return value

    @field_validator("limits")
    @classmethod
    def validate_limits(cls, value):
        if value is None:
            return value
        allowed = {"hn", "techcrunch", "arxiv"}
        unknown = set(value.keys()) - allowed
        if unknown:
            raise ValueError(f"Unknown limit keys: {', '.join(sorted(unknown))}")
        for key, limit in value.items():
            if not isinstance(limit, int) or limit < 1 or limit > 20:
                raise ValueError(f"Limit for {key} must be between 1 and 20")
        return value


class DigestPreviewResponse(BaseModel):
    mock: bool
    message: str
    items: list[DigestPreviewItem]
    sources: dict[str, bool]
    tip: str | None
    warnings: list[str] | None = None
