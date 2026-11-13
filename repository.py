
from typing import Optional, List, Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from exceptions import (
    AssetNotFoundError,
    DuplicateAssetError
)

from models import db, Asset, AssetTag
from domain import AssetData


class AssetRepository:

    # 1. Convert SQLAlchemy Asset into Domain AssetData
    def asset_to_dict(self, asset: Asset) -> dict[str, Any]:

        data = asset.to_dict()

        # Include only Active tags
        data["tags"] = [
            tag.to_dict()
            for tag in asset.tags
            if tag.status == "Active"
        ]

        # Convert into Domain object
        domain_asset = AssetData.from_dict(data)

        return domain_asset.to_dict()


    # 2. Create Asset
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


    # 3. Get Active Asset By ID
    def get_by_id(self, asset_id: int) -> Asset:

        asset = db.session.get(Asset, asset_id)

        if asset is None or asset.status != "Active":
            raise AssetNotFoundError(
                f"Active asset with ID {asset_id} not found"
            )

        return asset


    # 4. Get All Active Assets / Filter Assets
    def list(
        self,
        asset_type: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[dict[str, Any]]:

        # Only retrieve active assets
        query = select(Asset).where(
            Asset.status == "Active"
        )

        # Filter by asset category
        if asset_type:
            query = query.where(
                Asset.category == asset_type
            )

        # Filter by active asset tags
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

        assets = list(result.scalars().all())

        return [
            self.asset_to_dict(asset)
            for asset in assets
        ]


    # 5. Update Asset
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


    # 6. Deactivate Asset and All Its Active Tags
    def deactivate(self, asset: Asset) -> Asset:

        try:

            # Deactivate the asset
            asset.status = "Inactive"
            asset.updatedBy = "system"

            # Deactivate all associated active tags
            for tag in asset.tags:

                if tag.status == "Active":

                    tag.status = "Inactive"
                    tag.updatedBy = "system"

            db.session.commit()

            return asset

        except SQLAlchemyError:
            db.session.rollback()
            raise


    # 7. Add Multiple Asset Tags
    def add_tags(
        self,
        asset_id: int,
        tags: List[str]
    ) -> List[AssetTag]:

        # Ensure asset exists and is active
        self.get_by_id(asset_id)

        try:

            created_tags: List[AssetTag] = []

            for tag in tags:

                # Check whether tag already exists
                existing_tag_query = select(
                    AssetTag
                ).where(
                    AssetTag.asset_id == asset_id,
                    AssetTag.tag == tag
                )

                existing_tag = db.session.execute(
                    existing_tag_query
                ).scalar_one_or_none()

                if existing_tag:

                    # Skip already active tags
                    if existing_tag.status == "Active":
                        continue

                    # Reactivate previously deactivated tag
                    existing_tag.status = "Active"
                    existing_tag.updatedBy = "system"

                    created_tags.append(existing_tag)

                else:

                    # Create a new tag
                    asset_tag = AssetTag(
                        asset_id=asset_id,
                        tag=tag,
                        createdBy="system",
                        updatedBy="system",
                        status="Active"
                    )

                    db.session.add(asset_tag)

                    created_tags.append(asset_tag)

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


    # 8. Get Active Asset Tags
    def get_tags(self, asset_id: int) -> List[AssetTag]:

        # Ensure parent asset is active
        self.get_by_id(asset_id)

        query = select(AssetTag).where(
            AssetTag.asset_id == asset_id,
            AssetTag.status == "Active"
        ).order_by(AssetTag.id)

        result = db.session.execute(query)

        return list(result.scalars().all())
