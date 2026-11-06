
from typing import Optional, List, Any

from sqlalchemy import select
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
    ) -> List[Asset]:

        query = select(Asset).where(
            Asset.status == "Active"
        )

        if asset_type:
            query = query.where(
                Asset.category == asset_type
            )

        if tag:
            tag_subquery = select(
                AssetTag.asset_id
            ).where(
                AssetTag.tag == tag,
                AssetTag.status == "Active"
            )

            query = query.where(
                Asset.id.in_(tag_subquery)
            )

        result = db.session.execute(
            query.order_by(Asset.id)
        )

        return list(result.scalars().all())

    # 4. Update Asset
    def update(
        self,
        asset: Asset,
        update_data: dict[str, Any]
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
        tags: List[str]
    ) -> List[AssetTag]:

        try:
            existing_tags_query = select(AssetTag).where(
                AssetTag.asset_id == asset_id,
                AssetTag.status == "Active"
            )

            existing_tags = db.session.execute(
                existing_tags_query
            ).scalars().all()

            existing_tag_names = {
                item.tag for item in existing_tags
            }

            created_tags: List[AssetTag] = []

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
    def get_tags(self, asset_id: int) -> List[AssetTag]:

        query = select(AssetTag).where(
            AssetTag.asset_id == asset_id,
            AssetTag.status == "Active"
        ).order_by(AssetTag.id)

        result = db.session.execute(query)

        return list(result.scalars().all())
