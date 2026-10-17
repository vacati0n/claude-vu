# Feature Request — Knowledge Management Loop: Learn From Run Evidence

## Request

Give the framework a closed knowledge loop, so that what one run learns the hard way reaches the
agents of later runs without an operator carrying it by hand. Today the loop is open:

- Every rejected artifact is recorded (`validation_failed` events in `runs/<run>/events.jsonl`, each
  naming the failing check IDs; 29 across 24 runs on disk). Gate rejections and rollbacks are
  recorded too (`rollback_scheduled` events, `gate-rejection` entries in `recovery-ledger.json`).
- None of that reaches a later dispatch. Every invocation envelope carries
  `memory_slice: {hydrated: false, reason: "memory hydration not requested by this run"}`, and the
  context slice excludes `memory/*`. `memory/memory-resolver.md` and `config/runtime.md`
  ("Memory Loading", "Writeback Policy") specify hydration and fingerprint-keyed upsert, but no
  runtime code implements either.
- As a result the same mechanical rejection recurs run after run (for example the vendor-string
  check `C3.2` and the scope check `C7.1`), and the operator keeps private notes to warn agents.

## Expected outcome

1. **Harvest.** A runtime capability that reads recorded run evidence (events, recovery ledgers,
   validation reports) and distils it into *lessons*: one lesson per recurring failure pattern,
   keyed by a deterministic semantic fingerprint (artifact type + check ID, or gate + phase), with
   occurrence count, distinct-run count, first and last seen, the check's own description, and
   references to the evidence. Re-harvesting unchanged evidence is idempotent (fingerprint upsert).
2. **Govern.** Lessons live in a governed store under `memory/` with a status lifecycle
   (`candidate`, `active`, `retired`), an owner, and a rationale. A lesson becomes eligible for
   hydration when it is explicitly approved, or automatically when it recurs in at least a
   configured number of distinct runs. An operator can approve, retire, or annotate a lesson
   (add a human-written remedy) from the CLI. Nothing is deleted; retired lessons keep history.
3. **Recall.** `dispatch` hydrates the lessons relevant to the phase being dispatched — matched by
   the phase's output artifact and phase identifier — into the envelope's `memory_slice` and into a
   short "Lessons from earlier runs" section of the dispatch prompt, ranked and capped so the
   prompt grows by a bounded amount.
4. **Measure.** The loop reports whether it is working: for each lesson, how often the same failure
   recurred in a dispatch that had already been shown the lesson. Execution metrics record lessons
   hydrated per invocation.
5. **Close the loop automatically.** Harvest runs when a run aggregates, so a run's lessons are
   available to the next run with no operator step.

## Acceptance intent

- A phase whose artifact type has an eligible lesson receives it in both envelope and prompt.
- A run planned before this change, or a run planned with hydration switched off, dispatches
  byte-identically to today (no replay, verifier, or idempotency key changes outcome).
- Harvesting the current `runs/` produces lessons for the recorded `C3.2`- and `C7.1`-type failures.
- Harvesting twice over unchanged evidence produces an identical store.

## Constraints

- Additive only: gates, validators, artifact contracts, Phase Model tables, and agent module text
  are unchanged. The runtime never calls a model; lessons are derived mechanically from evidence.
- Standard library only; no vector store, embedding, or network dependency.
