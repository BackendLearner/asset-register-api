
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

    tags: list[AssetTagData] = field(default_factory=list)

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
