# Architecture Context — Lesson Store as an Open Knowledge Format Bundle

## The current store

- `runtime/knowledge.py` (FC-022) owns the store through three pieces:
  - `load_store(root)` returns the document `{schema, lessons: [...]}`, or None.
  - `write_store(root, data)` writes canonical bytes atomically, through a temporary file and
    `os.replace`, and only when the bytes differ.
  - `StoreLock` is an exclusive lock file, `memory/lessons/lessons.store.lock`.

  Harvest, governance, recall, effectiveness, the report and the aggregation step all go through
  `load_store` and `write_store`. If their dict interface stays the same, every caller stays
  unchanged.
- A lesson record has a closed field list (`LESSON_FIELDS`):
  - `lesson_id`: `L-` plus 10 hex characters of the fingerprint digest;
  - `fingerprint`, `kind`, `artifact_type`, `check_id`, `check_description`, `check_severity`,
    `gate`, `phases`, `occurrences`, `distinct_runs`, `first_seen`, `last_seen`;
  - `evidence`: run-relative references such as `runs/<run>/events.jsonl#E-0029`;
  - `evidence_state`, `status`, `owner`, `rationale`, `remedy`;
  - `history`: governance actions, each with an actor and a time.

  Timestamps have the form `YYYY-MM-DDTHH:MM:SSZ`.
- `render_section` builds the bounded, labelled prompt section from lesson records, and
  neutralises every field (CR-005). It must receive the same records as before.

## OKF v0.2 essentials

- **Files.** `index.md` and `log.md` are reserved. Every other `.md` is a concept document.
- **Frontmatter.** It is delimited by `---`, and `type` is the only required key. Consumers must
  preserve unknown keys.
- **Provenance and trust fields:**
  - `sources` entries require `resource`;
  - `generated` requires `by`;
  - `verified` is a list of `{by, at}`, and a bare map counts as one entry;
  - `status` defaults to `stable`;
  - `stale_after` is an absolute instant.
- **Actors** take one of three forms: `<producer>/<version>`, `human:<id>` or `process:<id>`.
- **index.md.** A root `index.md` may carry only one frontmatter key, `okf_version: "0.2"`. Its
  body is `# Heading` sections of `* [Title](url) - desc` entries.
- **log.md.** It starts with `# Title`, followed by `## YYYY-MM-DD` groups, newest first. Entries
  have the form `* **Creation|Update|Deprecation**: ...`.
- **§11 conformance:**
  - every non-reserved `.md` has parseable frontmatter;
  - every frontmatter block has a non-empty `type`;
  - the reserved files follow §8 and §9.

## Constraints from the codebase

- The standard library has no YAML parser. The change needs a deterministic writer, and a parser
  for the subset that the writer emits. The conformance check must parse the frontmatter it judges.
- `omn_agent/source.py` excludes paths by fnmatch on the name of each path part
  (`EXCLUDE_PATTERNS`, today `lessons.store.*`). That pattern does not cover a bundle of `index.md`,
  `log.md` and `L-*.md` files, and generic names such as `index.md` cannot be excluded by name
  alone.
- `runtime/optimize_memory.py` rewrites `memory/*.md` to reduce token cost. It skips three kinds of
  file: denied path segments, denied names, and files that declare themselves generated.
- The memory directory is excluded from the context slice (`memory/*`), so the bundle's documents
  are not slice members.
- Tests in `tests/test_knowledge.py` reference `STORE_REL`, the JSON file name, and the
  `lessons.store.*` exclusion. The backward-compatibility tests compare a dispatch by the 0.9.0
  runtime with a current one.
- `change_proposal_validator.py` F9 validates release checklist items per proposal, and requires
  only the mandatory items. A new mandatory item would therefore invalidate every recorded proposal.

## Authoring rules

- Artifact validators reject the substring of the host vendor name (check `C3.2`), so write paths
  without the dot-directory prefix.
- Never edit `runs/` evidence.
- Edit the framework directory, then run `python tests/test_bundled_payload.py --sync`.
