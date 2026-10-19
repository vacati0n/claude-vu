# Business Intent — Lesson Store as an Open Knowledge Format Bundle

## Problem

The framework's lessons hold what it has learned about what goes wrong in runs, and they are
locked in a private JSON schema. Three things follow from that:
- operators cannot read the lessons as documents;
- other tools cannot consume them;
- nothing in the file tells an outside reader who produced a lesson or who confirmed it.

## Intent

Store the framework's learned knowledge in an open, vendor-neutral knowledge format, so that it is
portable and can be reviewed. The change must not lose any governance or behaviour that the
knowledge loop has today.

## Success

- The lesson store is a conformant OKF v0.2 bundle, and a deterministic check proves it.
- Each lesson states, in the format's own terms, where it came from (`sources`, `generated`) and
  how far it can be trusted (`verified`, `status`).
- At dispatch, agents are shown exactly the same lesson text as before.
- No gate, validator, or acceptance rule is weakened, and every verifier stays at its recorded
  baseline.

## Non-goals

- Publishing the bundle outside the repository, or shipping it to installed copies.
- Changing which lessons are harvested, when they become eligible, or how they are ranked.
- Converting any other `memory/` document to OKF.
