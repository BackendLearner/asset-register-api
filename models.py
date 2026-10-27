
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Asset(db.Model):
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)

    asset_name = db.Column(db.String(100), nullable=False)
    asset_tag = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    purchase_cost = db.Column(db.Float)

    createdAt = db.Column(
        db.DateTime, nullable=False, default=utc_now
    )
    updatedAt = db.Column(
        db.DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )
    createdBy = db.Column(
        db.String(100), nullable=False, default="system"
    )
    updatedBy = db.Column(
        db.String(100), nullable=False, default="system"
    )
    status = db.Column(
        db.String(30), nullable=False, default="Active"
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
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "updatedAt": self.updatedAt.isoformat() if self.updatedAt else None,
            "createdBy": self.createdBy,
            "updatedBy": self.updatedBy,
            "status": self.status,
        }

    
class AssetTag(db.Model):
    __tablename__ = "asset_tags"

    id = db.Column(db.Integer, primary_key=True)

    asset_id = db.Column(
        db.Integer,
        db.ForeignKey("assets.id"),
        nullable=False,
        index=True,
    )

    tag = db.Column(db.String(100), nullable=False)

    createdAt = db.Column(
        db.DateTime, nullable=False, default=utc_now
    )
    updatedAt = db.Column(
        db.DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )
    createdBy = db.Column(
        db.String(100), nullable=False, default="system"
    )
    updatedBy = db.Column(
        db.String(100), nullable=False, default="system"
    )
    status = db.Column(
        db.String(30), nullable=False, default="Active"
    )

    __table_args__ = (
        db.UniqueConstraint("asset_id", "tag", name="uq_asset_tag"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "asset_id": self.asset_id,
            "tag": self.tag,
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "updatedAt": self.updatedAt.isoformat() if self.updatedAt else None,
            "createdBy": self.createdBy,
            "updatedBy": self.updatedBy,
            "status": self.status,
        }

