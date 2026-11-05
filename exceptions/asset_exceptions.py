class AssetError(Exception):
    """Base exception for asset-related errors."""
    pass


class AssetNotFoundError(AssetError):
    """Raised when an asset is not found."""
    pass


class DuplicateAssetError(AssetError):
    """Raised when a duplicate asset is created."""
    pass