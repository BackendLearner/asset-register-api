
from datetime import date
from typing import Optional

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator
)

class AssetCreate(BaseModel):

    asset_name: str = Field(
        min_length=1,
        max_length=100
    )

    asset_tag: str = Field(
        min_length=1,
        max_length=50
    )

    category: str = Field(
        min_length=1,
        max_length=100
    )

    location: Optional[str] = Field(
        default=None,
        max_length=100
    )

    purchase_date: Optional[date] = None

    purchase_cost: Optional[float] = Field(
        default=None,
        ge=0
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )


class AssetUpdate(BaseModel):

    asset_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    asset_tag: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    category: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    location: Optional[str] = Field(
        default=None,
        max_length=100
    )

    purchase_date: Optional[date] = None

    purchase_cost: Optional[float] = Field(
        default=None,
        ge=0
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    @field_validator(
        "asset_name",
        "asset_tag",
        "category"
    )
    @classmethod
    def reject_null_required_fields(cls, value):

        if value is None:
            raise ValueError(
                "This field cannot be null"
            )

        return value


class AssetTagCreate(BaseModel):

    tags: list[str] = Field(
        min_length=1,
        max_length=50
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, tags):

        if any(not tag for tag in tags):
            raise ValueError(
                "Every tag must be a non-empty string"
            )

        # Remove duplicate tags
        return list(dict.fromkeys(tags))
