
class AssetError(Exception):
    """Base exception for asset-related errors."""
    pass


class AssetNotFoundError(AssetError):
    """Raised when an asset is not found."""
    pass


class DuplicateAssetError(AssetError):
    """Raised when a duplicate asset is created."""
    pass


class AssetValidationError(AssetError):

    def __init__(self, errors):
        self.errors = errors
        super().__init__("Asset validation failed")
