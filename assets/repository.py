
from typing import Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from exceptions.asset_exceptions import (
    AssetNotFoundError,
    DuplicateAssetError
)

from models import db, Asset, AssetTag


class AssetRepository:

    # 1. Create Asset
    def create(self, asset: Asset) -> Asset:
        try:
            db.session.add(asset)
            db.session.commit()
            return asset

        except IntegrityError as exc:
            db.session.rollback()

            raise DuplicateAssetError(
                f"Asset tag '{asset.asset_tag}' already exists"
            ) from exc

        except SQLAlchemyError:
            db.session.rollback()
            raise

    # 2. Get Asset By ID
    def get_by_id(self, asset_id: int) -> Asset:

        asset = db.session.get(Asset, asset_id)

        if asset is None or asset.status != "Active":
            raise AssetNotFoundError(
                f"Active asset with ID {asset_id} not found"
            )

        return asset

    # 3. Get All Assets / Filter Assets
    def list(
        self,
        asset_type: Optional[str] = None,
        tag: Optional[str] = None
    ) -> list[Asset]:

        query = Asset.query.filter_by(status="Active")

        if asset_type:
            query = query.filter(
                Asset.category == asset_type
            )

        if tag:
            query = query.filter(
                Asset.id.in_(
                    db.session.query(AssetTag.asset_id).filter_by(
                        tag=tag,
                        status="Active"
                    )
                )
            )

        return query.order_by(Asset.id).all()

    # 4. Update Asset
    def update(
        self,
        asset: Asset,
        update_data: dict
    ) -> Asset:

        allowed_fields = {
            "asset_name",
            "asset_tag",
            "category",
            "location",
            "purchase_date",
            "purchase_cost"
        }

        try:
            for field, value in update_data.items():

                if field not in allowed_fields:
                    raise ValueError(
                        f"Field '{field}' cannot be updated"
                    )

                setattr(asset, field, value)

            asset.updatedBy = "system"

            db.session.commit()

            return asset

        except IntegrityError as exc:
            db.session.rollback()

            raise DuplicateAssetError(
                "Asset update violates a database constraint"
            ) from exc

        except SQLAlchemyError:
            db.session.rollback()
            raise

    # 5. Deactivate Asset
    def deactivate(self, asset: Asset) -> Asset:

        try:
            asset.status = "Inactive"
            asset.updatedBy = "system"

            db.session.commit()

            return asset

        except SQLAlchemyError:
            db.session.rollback()
            raise

    # 6. Add Asset Tags
    def add_tags(
        self,
        asset_id: int,
        tags: list[str]
    ) -> list[AssetTag]:

        try:
            existing_tags = AssetTag.query.filter_by(
                asset_id=asset_id,
                status="Active"
            ).all()

            existing_tag_names = {
                item.tag for item in existing_tags
            }

            created_tags = []

            for tag in tags:
                if tag not in existing_tag_names:

                    asset_tag = AssetTag(
                        asset_id=asset_id,
                        tag=tag,
                        createdBy="system",
                        updatedBy="system"
                    )

                    db.session.add(asset_tag)
                    created_tags.append(asset_tag)

                    existing_tag_names.add(tag)

            db.session.commit()

            return created_tags

        except IntegrityError as exc:
            db.session.rollback()

            raise DuplicateAssetError(
                f"Duplicate tag detected for asset ID {asset_id}"
            ) from exc

        except SQLAlchemyError:
            db.session.rollback()
            raise

    # 7. Get Asset Tags
    def get_tags(self, asset_id: int) -> list[AssetTag]:

        return AssetTag.query.filter_by(
            asset_id=asset_id,
            status="Active"
        ).order_by(AssetTag.id).all()
