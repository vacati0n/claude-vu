"""Service configuration loading.

Reads a JSON object describing service configuration and validates it into
an immutable ``Config`` value. Standard library only; no environment-variable
overrides, no other file formats, and no reload support are implemented,
per the accepted change's explicit exclusions.
"""
import json
from dataclasses import dataclass

from app.errors import ConfigError

_ALLOWED_FIELDS = {"port", "host", "debug"}
_MIN_PORT = 1
_MAX_PORT = 65535
_DEFAULT_HOST = "localhost"
_DEFAULT_DEBUG = False


@dataclass(frozen=True)
class Config:
    """Immutable service configuration value."""

    port: int
    host: str
    debug: bool


def load_config(path: str) -> Config:
    """Load and validate service configuration from a JSON file at ``path``.

    Raises ``ConfigError`` for any violation: missing file, invalid JSON,
    a non-object JSON root, an unknown field, a missing required field, a
    wrong-typed field, or a port outside 1..65535. Each message names the
    offending field or condition.
    """
    try:
        with open(path, "r", encoding="utf-8") as config_file:
            raw_text = config_file.read()
    except OSError as exc:
        raise ConfigError(f"config file not found or unreadable: {path}") from exc

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON in config file {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError("config root must be a JSON object")

    unknown_fields = sorted(set(data) - _ALLOWED_FIELDS)
    if unknown_fields:
        raise ConfigError(f"unknown field(s): {', '.join(unknown_fields)}")

    if "port" not in data:
        raise ConfigError("missing required field 'port'")

    port = data["port"]
    if isinstance(port, bool) or not isinstance(port, int):
        raise ConfigError("field 'port' must be an integer")
    if not (_MIN_PORT <= port <= _MAX_PORT):
        raise ConfigError(
            f"field 'port' out of range {_MIN_PORT}..{_MAX_PORT}: {port}"
        )

    host = data.get("host", _DEFAULT_HOST)
    if not isinstance(host, str):
        raise ConfigError("field 'host' must be a string")

    debug = data.get("debug", _DEFAULT_DEBUG)
    if not isinstance(debug, bool):
        raise ConfigError("field 'debug' must be a boolean")

    return Config(port=port, host=host, debug=debug)
