from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class AssetTagData:
    id: Optional[int] = None
    asset_id: Optional[int] = None
    tag: str = ""

    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    createdBy: str = "system"
    updatedBy: str = "system"
    status: str = "Active"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id"),
            asset_id=data.get("asset_id"),
            tag=data.get("tag", ""),
            createdAt=(
                datetime.fromisoformat(data["createdAt"])
                if data.get("createdAt") else None
            ),
            updatedAt=(
                datetime.fromisoformat(data["updatedAt"])
                if data.get("updatedAt") else None
            ),
            createdBy=data.get("createdBy", "system"),
            updatedBy=data.get("updatedBy", "system"),
            status=data.get("status", "Active")
        )

    def to_dict(self):
        return {
            "id": self.id,
            "asset_id": self.asset_id,
            "tag": self.tag,
            "createdAt": (
                self.createdAt.isoformat()
                if self.createdAt else None
            ),
            "updatedAt": (
                self.updatedAt.isoformat()
                if self.updatedAt else None
            ),
            "createdBy": self.createdBy,
            "updatedBy": self.updatedBy,
            "status": self.status
        }


@dataclass
class AssetData:
    id: Optional[int] = None
    asset_name: str = ""
    asset_tag: str = ""
    category: str = ""

    location: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_cost: Optional[float] = None

    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    createdBy: str = "system"
    updatedBy: str = "system"
    status: str = "Active"

    # One asset can have multiple tags
    tags: list[AssetTagData] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id"),
            asset_name=data.get("asset_name", ""),
            asset_tag=data.get("asset_tag", ""),
            category=data.get("category", ""),
            location=data.get("location"),

            purchase_date=(
                date.fromisoformat(data["purchase_date"])
                if data.get("purchase_date") else None
            ),

            purchase_cost=data.get("purchase_cost"),

            createdAt=(
                datetime.fromisoformat(data["createdAt"])
                if data.get("createdAt") else None
            ),

            updatedAt=(
                datetime.fromisoformat(data["updatedAt"])
                if data.get("updatedAt") else None
            ),

            createdBy=data.get("createdBy", "system"),
            updatedBy=data.get("updatedBy", "system"),
            status=data.get("status", "Active"),

            tags=[
                AssetTagData.from_dict(tag)
                if isinstance(tag, dict)
                else AssetTagData(tag=tag)
                for tag in data.get("tags", [])
            ]
        )

    def to_dict(self):
        return {
            "id": self.id,
            "asset_name": self.asset_name,
            "asset_tag": self.asset_tag,
            "category": self.category,
            "location": self.location,

            "purchase_date": (
                self.purchase_date.isoformat()
                if self.purchase_date else None
            ),

            "purchase_cost": self.purchase_cost,

            "createdAt": (
                self.createdAt.isoformat()
                if self.createdAt else None
            ),

            "updatedAt": (
                self.updatedAt.isoformat()
                if self.updatedAt else None
            ),

            "createdBy": self.createdBy,
            "updatedBy": self.updatedBy,
            "status": self.status,

            "tags": [
                tag.to_dict() for tag in self.tags
            ]
        }