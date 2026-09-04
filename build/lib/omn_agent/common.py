"""Shared result model: exit codes, findings, reports, and errors.

Every command builds a Report and finishes through Report.finish(), so the
output categories (SUCCESS / WARNING / ERROR / INVALID TARGET) and the exit
code are decided in exactly one place.
"""

from __future__ import annotations

import dataclasses
import enum
import sys


class ExitCode(enum.IntEnum):
    OK = 0
    INVALID_TARGET = 1        # missing path / not a repo / bad arguments about the target
    INCOMPLETE = 2            # installation or configuration incomplete
    VALIDATION_FAILED = 3     # post-install or standalone validation failed
    INCOMPATIBLE = 4          # existing state cannot be safely acted on
    DRY_RUN = 5               # dry-run finished; nothing was written
    PERMISSION_DENIED = 6     # filesystem permission error
    UNEXPECTED = 7            # unexpected error (bug, I/O, network)
    APPROVAL_REQUIRED = 8     # a side-effecting step was not approved


class Severity(enum.IntEnum):
    SUCCESS = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    INVALID = 4               # invalid target -- stronger than ERROR in the summary

    @property
    def label(self) -> str:
        return {
            Severity.SUCCESS: "SUCCESS",
            Severity.INFO: "INFO",
            Severity.WARNING: "WARNING",
            Severity.ERROR: "ERROR",
            Severity.INVALID: "INVALID TARGET",
        }[self]


@dataclasses.dataclass
class Finding:
    severity: Severity
    code: str                 # stable machine-readable code, e.g. "V-ENTRYPOINT"
    message: str
    hint: str | None = None


class OmnError(Exception):
    """A named, expected failure that maps directly onto an exit code."""

    def __init__(self, exit_code: ExitCode, message: str, hint: str | None = None):
        super().__init__(message)
        self.exit_code = exit_code
        self.message = message
        self.hint = hint


class Report:
    def __init__(self, command: str, target: str):
        self.command = command
        self.target = target
        self.findings: list[Finding] = []

    def add(self, severity: Severity, code: str, message: str, hint: str | None = None):
        self.findings.append(Finding(severity, code, message, hint))

    def success(self, code: str, message: str):
        self.add(Severity.SUCCESS, code, message)

    def info(self, code: str, message: str):
        self.add(Severity.INFO, code, message)

    def warning(self, code: str, message: str, hint: str | None = None):
        self.add(Severity.WARNING, code, message, hint)

    def error(self, code: str, message: str, hint: str | None = None):
        self.add(Severity.ERROR, code, message, hint)

    @property
    def worst(self) -> Severity:
        return max((f.severity for f in self.findings), default=Severity.SUCCESS)

    def count(self, severity: Severity) -> int:
        return sum(1 for f in self.findings if f.severity == severity)

    def summary_label(self) -> str:
        worst = self.worst
        if worst == Severity.INFO:
            return "SUCCESS"
        return worst.label

    def print(self, stream=None):
        stream = stream or sys.stdout
        print(f"omn-agent {self.command}  target: {self.target}", file=stream)
        for f in self.findings:
            print(f"  [{f.severity.label:<14}] {f.code}: {f.message}", file=stream)
            if f.hint:
                print(f"  {'':<17} hint: {f.hint}", file=stream)
        counts = ", ".join(
            f"{self.count(s)} {s.label.lower()}"
            for s in (Severity.ERROR, Severity.WARNING)
            if self.count(s)
        )
        print(f"RESULT: {self.summary_label()}" + (f"  ({counts})" if counts else ""),
              file=stream)

    def finish(self, *, ok_code: ExitCode = ExitCode.OK,
               error_code: ExitCode = ExitCode.VALIDATION_FAILED) -> ExitCode:
        """Print the report and translate its worst severity into an exit code."""
        self.print()
        worst = self.worst
        if worst == Severity.INVALID:
            return ExitCode.INVALID_TARGET
        if worst == Severity.ERROR:
            return error_code
        return ok_code
