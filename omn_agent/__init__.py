"""omn-agent -- bootstrap, installer, and orchestration CLI for the Omn-Agent framework.

This package is the *bootstrap* side of the framework: it installs, validates,
repairs, and upgrades the framework payload in a target repository, and it
prepares/approves work for the framework's own *runtime*
(``.omn-agent/runtime/framework_runtime.py``), which it never reimplements.
"""

__version__ = "0.1.0"

# Version of the install-manifest / bootstrap.json schema this tool reads and
# writes. A target whose recorded schemaVersion is newer than this is treated
# as incompatible (never downgraded in place).
SCHEMA_VERSION = 1
