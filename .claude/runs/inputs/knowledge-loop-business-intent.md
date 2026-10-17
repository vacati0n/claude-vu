# Business Intent — Knowledge Management Loop

## Problem

The framework forgets. Each run's agents start with the same context as the first run ever did,
so mechanical mistakes that a validator already caught in earlier runs are repeated, each costing a
charged attempt (three per phase), a retry dispatch, and operator time. The only memory of these
lessons is the operator's private notes, which other operators and installed copies do not have.

## Intent

Make the framework measurably better with use: every rejection a run records becomes knowledge the
next run's agents see before they write, with governance so that only recurring or approved lessons
are shown and stale ones can be retired.

## Success

- Lessons are harvested from existing run evidence without operator authoring.
- A phase whose artifact has a recorded recurring failure is told about it at dispatch.
- The framework can report, per lesson, whether the failure recurred after agents were warned —
  the evidence that learning is happening.
- No gate, validator, or acceptance rule is weakened; every verifier stays at its recorded baseline.

## Non-goals

- Model fine-tuning, embeddings, or any model call by the runtime.
- Automatically changing validators, templates, or agent text from lessons.
- Harvesting from sources other than recorded run evidence (chat transcripts, external tickets).
