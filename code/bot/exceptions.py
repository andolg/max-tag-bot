class AlreadyExistsException(Exception):
    """Indicates that something already exists in storage."""
    pass
class NotFoundException(Exception):
    """Indicates that something was not found in storage."""
    pass