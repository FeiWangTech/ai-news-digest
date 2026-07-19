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
    html: str


class DigestSendRequest(DigestPreviewRequest):
    recipient: str

    @field_validator("recipient")
    @classmethod
    def validate_recipient(cls, value: str) -> str:
        if value is None or not isinstance(value, str):
            raise ValueError("Recipient email is required")
        value = value.strip()
        if not value:
            raise ValueError("Recipient email is required")
        if any(c.isspace() for c in value):
            raise ValueError("Recipient email contains invalid whitespace")
        if value.count("@") != 1:
            raise ValueError("Recipient email must contain exactly one @")
        local, domain = value.split("@")
        if not local:
            raise ValueError("Recipient email local part is missing")
        if not domain:
            raise ValueError("Recipient email domain is missing")
        if "." not in domain:
            raise ValueError("Recipient email domain must contain a dot")
        if domain.startswith(".") or domain.endswith("."):
            raise ValueError("Recipient email domain cannot begin or end with a dot")
        return value


class DigestSendResponse(BaseModel):
    sent: bool
    message: str
    warnings: list[str] | None = None
