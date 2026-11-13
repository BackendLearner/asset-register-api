
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from exceptions import (
    AssetNotFoundError,
    DuplicateAssetError
)

from models import db, Asset, AssetTag
from domain import AssetData, AssetTagData


class AssetRepository:

    def _tag_to_domain(self, tag: AssetTag) -> AssetTagData:

        return AssetTagData(
            id=tag.id,
            asset_id=tag.asset_id,
            tag=tag.tag,
            createdAt=tag.createdAt,
            updatedAt=tag.updatedAt,
            createdBy=tag.createdBy,
            updatedBy=tag.updatedBy,
            status=tag.status
        )

    def _asset_to_domain(self, asset: Asset) -> AssetData:

        return AssetData(
            id=asset.id,
            asset_name=asset.asset_name,
            asset_tag=asset.asset_tag,
            category=asset.category,
            location=asset.location,
            purchase_date=asset.purchase_date,
            purchase_cost=asset.purchase_cost,
            createdAt=asset.createdAt,
            updatedAt=asset.updatedAt,
            createdBy=asset.createdBy,
            updatedBy=asset.updatedBy,
            status=asset.status,

            tags=[
                self._tag_to_domain(tag)
                for tag in asset.tags
                if tag.status == "Active"
            ]
        )


    def create(self, asset_data: AssetData) -> AssetData:

        asset = Asset(
            asset_name=asset_data.asset_name,
            asset_tag=asset_data.asset_tag,
            category=asset_data.category,
            location=asset_data.location,
            purchase_date=asset_data.purchase_date,
            purchase_cost=asset_data.purchase_cost,
            createdBy=asset_data.createdBy,
            updatedBy=asset_data.updatedBy,
            status=asset_data.status
        )

        try:
            db.session.add(asset)
            db.session.commit()

            return self._asset_to_domain(asset)

        except IntegrityError as exc:
            db.session.rollback()

            raise DuplicateAssetError(
                f"Asset tag '{asset.asset_tag}' already exists"
            ) from exc

        except SQLAlchemyError:
            db.session.rollback()
            raise


    def get_by_id(self, asset_id: int) -> AssetData:

        asset = db.session.get(Asset, asset_id)

        if asset is None or asset.status != "Active":
            raise AssetNotFoundError(
                f"Active asset with ID {asset_id} not found"
            )

        return self._asset_to_domain(asset)

    

    def list(
        self,
        asset_type: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[AssetData]:

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

        assets = result.scalars().all()

        return [
            self._asset_to_domain(asset)
            for asset in assets
        ]

   

    def update(
        self,
        asset_id: int,
        update_data: dict
    ) -> AssetData:

        allowed_fields = {
            "asset_name",
            "asset_tag",
            "category",
            "location",
            "purchase_date",
            "purchase_cost"
        }

        asset = db.session.get(Asset, asset_id)

        if asset is None or asset.status != "Active":
            raise AssetNotFoundError(
                f"Active asset with ID {asset_id} not found"
            )

        try:
            for field, value in update_data.items():

                if field not in allowed_fields:
                    raise ValueError(
                        f"Field '{field}' cannot be updated"
                    )

                setattr(asset, field, value)

            asset.updatedBy = "system"

            db.session.commit()

            return self._asset_to_domain(asset)

        except IntegrityError as exc:
            db.session.rollback()

            raise DuplicateAssetError(
                "Asset update violates a database constraint"
            ) from exc

        except SQLAlchemyError:
            db.session.rollback()
            raise


    def deactivate(self, asset_id: int) -> AssetData:

        asset = db.session.get(Asset, asset_id)

        if asset is None or asset.status != "Active":
            raise AssetNotFoundError(
                f"Active asset with ID {asset_id} not found"
            )

        try:
            asset.status = "Inactive"
            asset.updatedBy = "system"

            for tag in asset.tags:

                if tag.status == "Active":
                    tag.status = "Inactive"
                    tag.updatedBy = "system"

            db.session.commit()

            return self._asset_to_domain(asset)

        except SQLAlchemyError:
            db.session.rollback()
            raise

   

    def add_tags(
        self,
        asset_id: int,
        tags: List[str]
    ) -> List[AssetTagData]:

        # Verify parent asset exists and is active
        asset = db.session.get(Asset, asset_id)

        if asset is None or asset.status != "Active":
            raise AssetNotFoundError(
                f"Active asset with ID {asset_id} not found"
            )

        try:
            created_tags = []

            for tag in tags:

                existing_query = select(
                    AssetTag
                ).where(
                    AssetTag.asset_id == asset_id,
                    AssetTag.tag == tag
                )

                existing_tag = db.session.execute(
                    existing_query
                ).scalar_one_or_none()

                if existing_tag:

                    if existing_tag.status == "Active":
                        continue

                    existing_tag.status = "Active"
                    existing_tag.updatedBy = "system"

                    created_tags.append(existing_tag)

                else:
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

            return [
                self._tag_to_domain(tag)
                for tag in created_tags
            ]

        except IntegrityError as exc:
            db.session.rollback()

            raise DuplicateAssetError(
                f"Duplicate tag detected for asset ID {asset_id}"
            ) from exc

        except SQLAlchemyError:
            db.session.rollback()
            raise

   
    def get_tags(self, asset_id: int) -> List[AssetTagData]:

        asset = db.session.get(Asset, asset_id)

        if asset is None or asset.status != "Active":
            raise AssetNotFoundError(
                f"Active asset with ID {asset_id} not found"
            )

        query = select(AssetTag).where(
            AssetTag.asset_id == asset_id,
            AssetTag.status == "Active"
        ).order_by(AssetTag.id)

        result = db.session.execute(query)

        tags = result.scalars().all()

        return [
            self._tag_to_domain(tag)
            for tag in tags
        ]
