---
type: "Lesson"
title: "validation-check R7 on release-note.md"
description: "The version is a recognisable version string"
tags:
  - "validation-check"
  - "release-note.md"
  - "documentation-and-release-handoff"
sources:
  - resource: "../../runs/run-919c5d5cf156/events.jsonl"
  - resource: "../../runs/run-ae91e085f481/events.jsonl"
  - resource: "../../runs/run-efe092286625/events.jsonl"
generated:
  at: "2026-09-18T00:25:04Z"
  by: "knowledge-loop/1.0.0"
status: "draft"
lesson_record:
  lesson_id: "L-a1c32dc2c2"
  fingerprint: "check:release-note.md:R7"
  kind: "validation-check"
  check_id: "R7"
  check_description: "The version is a recognisable version string"
  check_severity: "Correctable"
  gate: null
  artifact_type: "release-note.md"
  phases:
    - "documentation-and-release-handoff"
  occurrences: 3
  distinct_runs: 3
  first_seen: "2026-08-28T06:24:52Z"
  last_seen: "2026-09-18T00:25:04Z"
  evidence:
    - "runs/run-919c5d5cf156/events.jsonl#E-0089"
    - "runs/run-ae91e085f481/events.jsonl#E-0083"
    - "runs/run-efe092286625/events.jsonl#E-0081"
  evidence_state: "current"
  status: "candidate"
  owner: "tech-lead"
  rationale: "harvested from recorded run evidence: the Validation Engine rejected this artifact type on this check"
  remedy: null
  history: []
---
# validation-check R7 on release-note.md

Summary: The version is a recognisable version string
