"""Install-manifest handling: the record of what the framework owns.

The manifest lives at ``.omn-agent/bootstrap/install-manifest.json`` and maps
each framework-managed file to the SHA-256 of its content *as installed*.
It is the sole basis for the overwrite-safety decision: a file whose current
hash matches its recorded hash is framework-managed and unmodified, and only
such files are ever updated in place.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
from pathlib import Path

from . import SCHEMA_VERSION, __version__
from .common import ExitCode, OmnError
from .source import MANIFEST_PATH


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def new_manifest(source: str) -> dict:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "toolVersion": __version__,
        "source": source,
        "initializedAt": _now(),
        "installedAt": None,
        "files": {},   # managed: rel path -> sha256 as installed
        "seeds": {},   # seeded:  rel path -> sha256 as first created
    }


def manifest_file(framework_dir: Path) -> Path:
    return framework_dir / MANIFEST_PATH


def load_manifest(framework_dir: Path) -> dict | None:
    """Load the manifest, or None when absent. Unreadable -> INCOMPATIBLE."""
    path = manifest_file(framework_dir)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise OmnError(
            ExitCode.INCOMPATIBLE,
            f"install manifest is unreadable: {path} ({exc})",
            hint="the manifest is the overwrite-safety record; refusing to act on "
                 "this installation. Restore the file from version control, or move "
                 "the .omn-agent directory aside and run 'omn-agent install' fresh")
    if not isinstance(data, dict) or not isinstance(data.get("files"), dict):
        raise OmnError(ExitCode.INCOMPATIBLE,
                       f"install manifest has an unexpected shape: {path}")
    recorded = data.get("schemaVersion", 0)
    if recorded > SCHEMA_VERSION:
        raise OmnError(
            ExitCode.INCOMPATIBLE,
            f"installation was written by a newer omn-agent (manifest schema "
            f"{recorded} > supported {SCHEMA_VERSION})",
            hint="upgrade the omn-agent tool itself, then re-run")
    return data


def save_manifest(framework_dir: Path, manifest: dict, *, installed: bool):
    manifest["toolVersion"] = __version__
    if installed:
        manifest["installedAt"] = _now()
    path = manifest_file(framework_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(path, (json.dumps(manifest, indent=2, sort_keys=True) + "\n")
                 .encode("utf-8"))


def atomic_write(path: Path, data: bytes):
    """Write via a temp file + rename so a crash never leaves a torn file."""
    tmp = path.with_name(path.name + ".tmp-omn")
    with open(tmp, "wb") as fh:
        fh.write(data)
    os.replace(tmp, path)
