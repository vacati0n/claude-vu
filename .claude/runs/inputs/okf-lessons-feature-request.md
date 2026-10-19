# Feature Request — Lesson Store as an Open Knowledge Format Bundle

## Request

Store the framework's harvested lessons in the Open Knowledge Format (OKF) v0.2, published at
https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md, instead of the
single JSON document `memory/lessons/lessons.store.json` introduced by FC-022.

Today every lesson lives in one framework-private JSON file (schema `framework.memory/lessons.v1`).
Only `runtime/knowledge.py` can read it. It carries no provenance or trust metadata that a third
party would understand, and it cannot be browsed, linked or reviewed as documents. OKF is an open,
vendor-neutral format built for this: a directory of markdown concept documents with YAML
frontmatter, plus reserved `index.md` and `log.md` files.

## Expected outcome

1. **Bundle.** The lesson store becomes an OKF bundle directory under `memory/lessons/`. The
   bundle has one markdown concept document per lesson, a root `index.md` that declares
   `okf_version: "0.2"`, and a `log.md` change log.
2. **Concept documents.** Each lesson document's YAML frontmatter carries the following:
   - non-empty `type`, `title`, `description` and `tags`;
   - `sources` (SPEC §5.1): one entry per run artifact the lesson was harvested from. Each entry
     has a required `resource`;
   - `generated` (§5.2): `{by, at}`, where `by` is an actor of the form `<producer>/<version>`;
   - `verified` (§5.3) where the lesson has been confirmed. An operator approval uses a
     `human:<id>` actor, and a machine confirmation uses a `process:<id>` actor;
   - `status` (§5.4): `draft`, `stable` or `deprecated`, mapped from the governance state
     (`candidate`, `active`, `retired`);
   - `stale_after` (§5.5) where it applies;
   - every other lesson field, kept as a producer extension key so that nothing FC-022 records is
     lost.

   Every timestamp is ISO 8601 with a UTC offset, and every actor follows §7.
3. **Same loop.** These parts read and write the bundle: harvest, governance (approve, retire,
   annotate), recall, effectiveness and the aggregation step. For the same lessons, the rendered
   prompt section (`render_section`) is byte-for-byte unchanged, including the CR-005
   neutralisation. Re-harvesting unchanged evidence leaves the bundle byte-identical.
4. **Conformance check.** The framework's verification tooling gains a deterministic check of the
   bundle against OKF §11, which can also be run standalone. The check confirms three things:
   - every non-reserved `.md` has parseable YAML frontmatter;
   - every frontmatter block has a non-empty `type`;
   - the reserved files follow §8 and §9 when they are present.
5. **Migration.** The 42 existing lessons are migrated into the bundle with their governance
   history intact, and the JSON store is removed.

## Constraints

- No run evidence under `runs/` is edited.
- Only the standard library is used; there is no third-party YAML dependency.
- The bundle stays out of the installed payload and the bundled mirror, as the JSON store did.
- The memory optimiser must not rewrite the bundle.
