class AppError(Exception):
    """Base class for application errors."""


class ConfigError(AppError):
    """Raised when service configuration fails to load or validate.

    The message names the offending field or condition (missing file,
    invalid JSON, missing required field, wrong type, out-of-range value,
    or unknown field).
    """
