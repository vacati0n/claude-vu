```yaml
design:
  designId: CKA-06-technical-design
  changeReference: CKA-06
  sourceInputs:
    - type: change-request
      reference: runs/inputs/cka-06-feature-request.md
    - type: execution-plan
      reference: runs/run-4c51600606df/states/execution-planning/artifacts/execution-plan.md
  producedBy: architect
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  decisionRecords: [D-001, D-007, D-008]
  consumesPlan: runs/run-4c51600606df/states/execution-planning/artifacts/execution-plan.md
  inputDigest: sha256:916928da1e2ad4f0df64d042bfe46181
  contextDigest: sha256:ea8b3b5e9812546f9b4054458bb8143e
```

## Metadata

- Feature or Change ID: CKA-06
- Author: architect
- Reviewers: omn-architect, omn-tech-lead
- Last Updated: 2026-09-05

Upstream identifier notation. The approved scope definition and the Scope and Planning Gate
decisions use identifier families that would collide with this package's own registers, so
they are cited here in a distinct form: approved scope items as `SC-001` to `SC-008`,
approved acceptance criteria as `AC-001` to `AC-014`, approved exclusions as `X-001` to
`X-007`, approved scope decisions as `SD-001` to `SD-006`, Scope Gate conditions as `SGC-1`
to `SGC-5`, and Planning Gate conditions as `PGC-1` to `PGC-5`. Every bare `S-nnn`, `F-nnn`,
`A-nnn`, `C-nnn`, `M-nnn`, `O-nnn`, `D-nnn`, `R-nnn`, `P-nnn`, and `Q-nnn` token resolves
against this package's own registers. `T-nnn` tokens are the supplied plan's and are cited,
never created.

Evidence basis. The current-state facts below were taken by direct read of five committed
files in the repository working tree: `docs/USER-GUIDE.md`, `docs/user-guide.html`,
`.github/workflows/verify.yml`, `tests/test_ci_workflow.py`, and `tests/test_omn_agent.py`.
No external system, repository host, or ticketing tool was contacted, and no file was
modified. The anchor baseline in Appendix B was enumerated from the committed published file
itself, not from any list supplied to this agent, as `T-009` requires.

## Objective

- Desired outcome: the operator handbook has one authored form, `docs/USER-GUIDE.md`, from
  which `docs/user-guide.html` is a pure build output, and the repository's verification
  workflow refuses a source change that lands without a regenerated published file.

- Architectural objectives:

  - The published file is a total function of the source file: no information reaches the
    published output except through the source or through a fixed renderer-held page shell,
    so a direct edit to the output has nowhere to survive (`S-004`, `S-037`).
  - The renderer's output is byte-stable under repetition, locale, dictionary ordering, and
    operating system, because the whole change rests on a byte comparison that is worthless
    if any of those vary (`S-005`, `S-020`).
  - Every value the published form carries that is not derivable from the source is moved
    into the source, on the line it belongs to, so that the tool holds a grammar and never
    holds document content (`S-009`, `S-010`, `S-032`).
  - The anchor identifier set the published file exposes today becomes an authored,
    stable property of the source rather than an accident of a slug algorithm (`S-030`,
    `S-031`).
  - The staleness verdict is attached to a verification surface that can block a merge, and
    is added without changing the surface's job topology (`S-012`, `S-019`, `S-035`,
    `S-036`).

- In scope: the source document's notation contract, the published document's generation
  contract, the renderer's determinism boundary, the placement of the drift check inside the
  existing verification workflow, and the sequencing those four impose on delivery.

- Out of scope: any change to runtime, gate-decision, or approval behaviour (`X-002`); any
  second documentation pair (`X-001`); editorial rewriting beyond resolving one-sided
  content (`X-003`); hosting the published handbook anywhere outside the repository
  (`X-004`); making the handbook's factual claims checkable against tool behaviour
  (`X-005`); an automated visual or structural regression check over the reading affordances
  (`X-006`); and removing the published handbook from version control (`X-007`). This change
  touches two shared boundaries — the contributor-facing authoring contract of the source
  document and the check-name contract of the verification workflow — so the exclusions above
  are what stop the impact surface expanding into either.

## Requirements Summary

Functional requirements:

- A tool reads `docs/USER-GUIDE.md` and writes `docs/user-guide.html` with no manual step
  between them (`S-005`).
- The same tool offers a mode that re-renders in memory, compares against the committed
  published file byte for byte, exits nonzero on a mismatch, and prints the regeneration
  command (`S-011`).
- The verification workflow runs that mode on every leg of its matrix (`S-012`, `S-019`).
- The published page announces at its top that it is generated, names its source file, and
  gives its regeneration command (`S-013`, `S-016`).
- The source expresses the navigation index, chapter labels, callout blocks, the chain
  diagram, code samples with distinguishable comment lines, and section anchors (`S-032`).
- Every anchor identifier the published file exposes before the change still resolves after
  it to the section carrying the same material (`S-030`, `S-031`).
- Contributor-facing documentation instructs regeneration and no longer instructs
  hand synchronisation (`S-014`).

Non-functional requirements:

- Byte identity of regenerated output across repeats in one environment and across both
  operating systems in the verification matrix, line endings included (`S-005`, `S-020`).
- No dependency outside the standard library (`S-006`, `S-028`).
- The source stays a document a contributor reads and edits as prose; adding a section, a
  callout, or a code sample does not mean hand-writing markup (`S-010`, `S-038`).
- The change is additive: no runtime surface, no gate-decision surface, no approval path
  (`S-018`).
- The verification surface keeps its exact job topology and its stable check names
  (`S-035`).

Acceptance criteria: the fourteen criteria `AC-001` to `AC-014` of the approved scope are
cited rather than restated (`S-021`, `S-025`, `S-026`, `S-027`, `S-029`). This design binds
most directly to `AC-001`, `AC-002`, `AC-003`, `AC-007`, `AC-008`, `AC-009`, `AC-010`,
`AC-011`, `AC-012`, and `AC-013`. The two criteria routed to this phase are `AC-008`, which
the anchor notation must satisfy, and `AC-012`, which the source notation must satisfy
(`S-024`, `S-033`, `S-034`).

## Current-State Assumptions and Constraints

### 4.1 Facts

| ID | Fact | Established by |
|---|---|---|
| F-001 | The handbook is published as `docs/USER-GUIDE.md` at 1051 lines and `docs/user-guide.html` at 1033 lines | Feature request; direct read of both files |
| F-002 | `docs/user-guide.html` declares exactly 21 distinct anchor identifiers: 9 on chapter section elements and 12 on in-chapter level-3 headings | Direct read; every `id` attribute in the file, enumerated in Appendix B |
| F-003 | The same file contains 21 internal link targets whose set is equal to those 21 identifiers, so its internal link graph is closed and complete | Direct read; every `href` beginning with a fragment marker |
| F-004 | No anchor identifier is the slug of its own heading text under any common slug algorithm; counter-examples include `trouble` for "Troubleshooting", `model` for "The mental model", and `flow-implement` for the heading numbered 4.1 | Direct read; pairwise comparison of each identifier against its heading |
| F-005 | The published navigation index carries 9 entries, and 4 of the 9 labels differ from the heading text they point at | Direct read of the navigation block against the chapter headings |
| F-006 | Each published chapter carries a label reading "Chapter N", where N is the ordinal already present as a numeric prefix in the corresponding source heading | Direct read of both files |
| F-007 | The published file carries 14 callout blocks, each opening with a short tag whose text appears nowhere in the corresponding source paragraph; one of the 14 carries an additional variant marker | Direct read of every callout element |
| F-008 | The source expresses the same asides as paragraphs opening with a bolded lead-in run; 20 such lines exist | Direct read; count of lines beginning with a bolded run |
| F-009 | `docs/USER-GUIDE.md` contains no link in bracket-and-parenthesis form and no blockquote line | Direct read; pattern search over the whole file returned zero matches for both |
| F-010 | The published file carries two chain diagrams, each a row of arrow-separated tokens with exactly one token marked as a gate, and each carrying a hand-written accessibility label that is not a mechanical join of its own tokens | Direct read of both chain elements and their labels |
| F-011 | The source carries both chains as fenced blocks with no info string, each holding a single arrow-separated line | Direct read of both fenced blocks |
| F-012 | The published file marks comment lines inside code samples with a dedicated span; the source expresses them as lines opening with a hash inside shell-tagged fences, and one line opening with a double slash inside a data-tagged fence | Direct read of both files |
| F-013 | One hash character inside a published code sample sits within a single-quoted argument value and is deliberately not marked as a comment | Direct read of the quality-scan code sample |
| F-014 | `.github/workflows/verify.yml` declares exactly six jobs: a discovery job, a tests job, two per-verifier matrix jobs, and two fan-in jobs | Direct read of the workflow |
| F-015 | The tests job renders its check name as a platform-suffixed name over a two-entry matrix covering ubuntu and windows, installs the package, and runs the unit-test suite by discovery | Direct read of the tests job |
| F-016 | `tests/test_ci_workflow.py` asserts that the workflow's job identifier set equals exactly that six-element set | Direct read, `test_job_topology_and_stable_names` |
| F-017 | The same module asserts that no filename matching the test-file or verifier-file patterns appears anywhere in the workflow text | Direct read, `test_no_curated_file_list` |
| F-018 | The same module asserts that the workflow's comment-stripped text contains neither a colour-suppression variable nor a failure-masking key | Direct read, `test_environment_and_permission_policy` |
| F-019 | The workflow's own header records that the ubuntu tests check is required from the first run, and that the windows tests check and both fan-in checks are advisory until a settings-only flip | Direct read of the workflow header |
| F-020 | `tests/test_ci_workflow.py` asserts that `README.md`, `docs/USER-GUIDE.md`, and `docs/user-guide.html` each contain all four stable check names and the workflow filename | Direct read, `DocumentationParity` |
| F-021 | `tests/test_omn_agent.py` asserts that `docs/user-guide.html`, lowercased, contains the name of the data-format distribution the installed runtime imports | Direct read, `test_user_guide_states_true_dependency_footprint` |
| F-022 | The published installation chapter carries a paragraph stating that the installed runtime files import that distribution and that the packaging manifest declares it; `docs/USER-GUIDE.md` carries no equivalent statement | Direct read of both installation sections |
| F-023 | The published troubleshooting table carries a row for the unresolved-import validation finding; the source troubleshooting table has no such row | Direct read of both troubleshooting tables |
| F-024 | The docstring of the parity test class in `tests/test_ci_workflow.py` describes the published handbook as hand-synced with the source | Direct read, class docstring |
| F-025 | No proof script under the framework runtime directory reads either handbook file | Direct read; repository-wide search for both handbook filenames returned only run evidence, backlog documents, change proposals, and the two test modules |
| F-026 | The repository has no line-ending attributes file at its root | Direct read; repository-root glob returned no match |
| F-027 | The repository has no `tools/` directory | Direct read; repository glob returned no match |
| F-028 | The source uses level-2 headings with ordinal prefixes 1 to 9 and, additionally, five lettered prefixes under ordinal 5, while the published file renders those five as level-3 headings inside the chapter-5 section | Direct read of both heading sets |
| F-029 | The published file opens with a title element and a style block and links an external font stylesheet; it declares no document-type marker and no outer document elements | Direct read of the file's first lines |
| F-030 | The published footer states that the guide is versioned at `docs/USER-GUIDE.md` | Direct read of the footer |
| F-031 | The published file wraps every table in a container element and marks a subset with a numeric-table class; in every marked table the first body column is numeric and in every unmarked table it is not | Direct read of all published tables |
| F-032 | `tests/test_omn_agent.py` additionally asserts the packaging manifest's declared dependency and the same distribution name in `README.md` | Direct read, `DependencyDeclarationTestCase` |
| F-033 | The workflow parity test extracts steps by positional index only from the discovery job and the two per-verifier jobs, never from the tests job | Direct read, `DiscoveryExpression` and `VerifierAssertionWrapper` |

### 4.2 Assumptions

| ID | Assumption | Why needed | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | The working-tree revision of the five files read is the revision this change is applied to | The anchor baseline and the committed-assertion inventory are taken from it | An anchor added after the read is absent from the baseline and can be dropped undetected; the baseline must be re-enumerated at reconciliation time | omn-tech-lead |
| A-002 | The hosted windows runner presents the committed published file with the bytes that were committed, rather than translating its line endings at checkout | The byte comparison on the windows leg compares against committed bytes | The windows leg fails permanently regardless of renderer correctness, until the two handbook paths are pinned against checkout translation | omn-qa |
| A-003 | A single regeneration command string, written with forward slashes, runs unmodified on both matrix platforms | One command form is embedded in the banner, in the failure output, and in contributor documentation | The banner, the failure output, and the documentation each state a per-platform form, and the single-string property `AC-003` asks for is lost | omn-qa |
| A-004 | Every item the reconciliation merges into the source is expressible in the notation this design defines, without a further construct | The notation is fixed before the resolution list is applied | The notation reopens after implementation has started, and the raw-markup measure and the authoring walkthrough are both taken against a moving target | omn-product-owner |
| A-005 | The two chain diagrams' accessibility labels are derived presentation under the recorded authored-content test, not authored content | Decides whether the chain construct needs an authored label slot | The chain construct gains one optional authored field, one more thing a contributor may write, and the published labels are preserved rather than regenerated | omn-product-owner |
| A-006 | The handbook carries no maintenance material able to hold the regeneration instruction, so the instruction lands in the generated banner and in `README.md` | Bounds the documentation surface this design sequences against | A third target exists and the instruction lands in three places rather than two | omn-documentation |
| A-007 | The committed published file's terminal byte sequence is reproducible under a single fixed newline policy in the renderer | The first regeneration must match the commit exactly for `AC-001` to pass without rewriting the target | The committed published file is rewritten once so its final bytes match the renderer's policy, which is a one-time deviation from "regeneration reproduces the commit" that must be recorded | omn-dev-1-implement |
| A-008 | No consumer outside this repository links to the published file's anchors in a form this change cannot enumerate | Bounds the anchor-preservation obligation to the enumerated set of 21 | An external link may break even though every enumerated identifier survives, and the obligation is wider than `AC-008` states | omn-product-owner |

### 4.3 Constraints

| ID | Class | Constraint | Hard or negotiable | Source |
|---|---|---|---|---|
| C-001 | structural | The source of record is `docs/USER-GUIDE.md`; `docs/user-guide.html` is its build output and is never authored directly | Hard | `SD-003`, `S-004` |
| C-002 | functional | Every anchor identifier the published file exposes before the change resolves, after it, to the section carrying the same material | Hard | `AC-008`, `F-002`, `F-003` |
| C-003 | structural | The renderer introduces no dependency outside the standard library | Hard | `S-006`, `S-028`, `F-032` |
| C-004 | quality-attribute | Regeneration is byte-identical across repeats in one environment and across both matrix platforms, line endings included | Hard | `S-020`, `AC-010`, `AC-011` |
| C-005 | structural | The verification workflow's job identifier set is unchanged; the drift check is a step inside the existing tests job | Hard | `F-014`, `F-016`, `PGC-1` |
| C-006 | structural | The drift step is expressed over the known build output, never over a curated list of files a future contributor must extend | Hard | `S-019`, `F-017` |
| C-007 | compliance | The change alters no runtime, gate-decision, or approval surface the backlog forbids altering | Hard | `S-018`, `X-002` |
| C-008 | migration | Every string a committed test asserts in the published file survives the reconciliation; such an item is resolved as merged into the source, never dropped | Hard | `F-020`, `F-021`, `F-032`, `SGC-1`, `PGC-5` |
| C-009 | functional | The published page announces at its top that it is generated, names its source file, and gives its regeneration command | Hard | `S-013`, `S-016`, `AC-009` |
| C-010 | quality-attribute | A contributor adds a section, a callout, or a code sample to the source using notation present in that file, without hand-writing markup | Negotiable | `SC-007`, `AC-012` |
| C-011 | quality-attribute | The count of raw-markup lines in the source does not rise | Negotiable | `AC-013`, `SGC-2`; reported rather than enforced where it conflicts with `C-002` |
| C-012 | structural | The workflow's effective text contains neither a colour-suppression variable nor a failure-masking key | Hard | `F-018` |
| C-013 | operability | The drift failure output carries the regeneration command as a string a contributor runs unmodified | Hard | `S-011`, `AC-003` |
| C-014 | security | The renderer reads only the two named handbook files and writes only the published file; check mode writes nothing at all | Hard | `S-011`, `C-007` |
| C-015 | structural | The five named reading affordances survive regeneration | Hard | `SC-004`, `AC-007`, `SD-001` |

## Architecture and Component Design

### 5.1 Impacted Modules

| ID | Module | Impact type | Basis | Interfaces affected | Confidence |
|---|---|---|---|---|---|
| M-001 | `tools/render_user_guide.py`, the handbook renderer | extension | F-027, S-005 | Its command-line surface: a default render mode and a check mode | confirmed |
| M-002 | `docs/USER-GUIDE.md`, the source handbook | contract-change | F-001, F-009, F-028 | The authoring notation a contributor writes against | confirmed |
| M-003 | `docs/user-guide.html`, the published handbook | contract-change | F-002, F-029, F-030 | Its anchor set, its affordance set, and its editing contract | confirmed |
| M-004 | The tests job of `.github/workflows/verify.yml` | extension | F-014, F-015, F-033 | The two platform-suffixed tests check names | confirmed |
| M-005 | The repository line-ending attributes file | operational-impact | F-026, A-002 | Checkout-time line-ending translation for the two handbook paths | speculative |
| M-006 | `tests/test_ci_workflow.py` | behavior-change | F-024, S-034 | None; every assertion is unchanged and only the module's own hand-sync sentence is corrected | confirmed |
| M-007 | `README.md` | extension | F-032, S-014 | The contributor instruction for the handbook pair | confirmed |
| M-008 | `tests/test_omn_agent.py` dependency-footprint assertions | no-change-verified | F-021, F-032 | The published-file assertion the reconciliation must keep passing | confirmed |
| M-009 | The packaging manifest | no-change-verified | F-032, C-003 | The declared dependency set, unchanged | confirmed |
| M-010 | The proof-script set under the framework runtime directory | no-change-verified | F-025 | None | confirmed |
| M-011 | The discovery job, the two per-verifier jobs, and the two fan-in jobs of the verification workflow | no-change-verified | F-014, F-033 | Their rendered check names, unchanged | confirmed |

`M-008` through `M-011` are recorded rather than omitted because a reader would reasonably
expect a change that edits the published handbook, adds a dependency-free tool, and touches
the verification workflow to disturb all four. `M-010` and `M-011` are the boundary
crossings this change makes and does not widen: the renderer is invoked from inside an
existing job and nothing in the verifier surface learns about it. `M-005` is speculative
because `A-002` cannot be established from the supplied context; `R-002` carries it.

### 5.2 Options Considered

The question every option answers is where the published form's non-derivable information
lives: the 21 anchor identifiers (`F-002`, `F-004`), the 4 divergent navigation labels
(`F-005`), and the 14 callout tags (`F-007`).

| Option | Structural change | Hard constraints | Impact surface | Reuse leverage | Quality attributes | Migration burden | Operability | Outcome |
|---|---|---|---|---|---|---|---|---|
| O-001 | Every non-derivable value is authored inline in the source on the line it belongs to, in one attribute construct; the renderer holds a grammar and a fixed page shell, never document content | All satisfied | 2 | 5 of 9 | C-010 satisfied; C-011 rises modestly; C-015 satisfied | 2 | One file to edit, one command to run; a new chapter needs no tool change | Selected |
| O-002 | The renderer carries mapping tables keyed by heading and paragraph text that supply the slugs, the navigation labels, and the callout tags; the source stays untouched prose | All satisfied | 3 | 4 of 9 | C-010 not met in effect; C-011 unchanged; C-015 satisfied | 3 | Every new chapter, renamed heading, or new callout requires a tool edit | Not selected |
| O-003 | A committed sidecar data file carries the same three maps and the renderer consumes it | All satisfied | 3 | 4 of 9 | C-010 not met; C-011 unchanged in the source but a second hand-kept file appears; C-015 satisfied | 3 | Two files must be kept in step by hand, which is the defect this change exists to remove | Not selected |
| O-004 | Slugs and navigation labels are derived by algorithm from heading text and the current values are allowed to change | Violated | 2 | 3 of 9 | C-010 satisfied; C-011 unchanged; C-015 partly met, navigation labels and anchors degrade | 2 | All 21 published anchors and the closed internal link graph break in one commit | Eliminated on C-002 |
| O-005 | The direction is inverted: the published file is the source and the Markdown handbook is generated from it | Violated | 2 | 1 of 9 | C-010 inverted, the contributor authors markup; C-011 not applicable; C-015 satisfied | 2 | The file contributors read and edit becomes the generated one | Eliminated on C-001 |

Impact surface counts modules the option gives `contract-change` or `dependency-change`.
Reuse leverage counts the capabilities in section 7 the option satisfies by `reuse-as-is` or
`reuse-extended`, out of nine surveyed. Migration burden counts contract-affecting changes
requiring a transition strategy. Criteria are applied in the order fixed by the reasoning
procedure: hard-constraint satisfaction first, then impact surface, then reuse leverage,
then quality attributes, then migration burden, then operability.

### 5.3 Selected Approach

- Selected: `O-001`.

- Structural change: the source document gains one attribute construct, written in braces at
  the end of the line whose value it supplies. On a heading it carries the section's anchor
  identifier and, where the navigation label differs from the heading text, that label. On a
  callout it carries the block's variant where one exists. Three further constructs are
  reused rather than invented: a callout is a blockquote whose leading bolded run is its tag,
  a chain diagram is a fenced block whose info string names it, and a code sample keeps the
  fenced form and info string it already has. Everything else the published form shows —
  the chapter labels, the navigation index, the numeric-table marking, the section nesting,
  the comment marking inside code samples — is derived by the renderer from what the source
  already contains. The renderer holds the page shell verbatim: the title, the style block,
  the font stylesheet link, the masthead, and the footer.

- Rationale: `O-001` is the only option that satisfies every hard constraint while keeping
  document content out of the tool. `C-002` eliminates `O-004` outright, because 21
  identifiers and a closed internal link graph (`F-002`, `F-003`) cannot survive derivation
  when not one of them is derivable (`F-004`). `C-001` eliminates `O-005`. Among the three
  survivors `O-001` has the smallest impact surface, the highest reuse leverage, and the only
  operability profile in which adding a chapter is a documentation act rather than a tool
  release. It is also the only survivor that satisfies `C-010`: under `O-002` a contributor
  who adds a chapter must edit a program to give it an anchor, which is worse than the markup
  `C-010` exists to avoid, and under `O-003` the contributor must keep two files in step by
  hand, which reproduces the defect this change removes.

- Highest-scoring rejected alternative and why it lost: `O-002`, the renderer-held mapping
  tables. It satisfies every hard constraint, reproduces all 21 anchors exactly, and leaves
  the source's raw-markup count untouched, which is the strongest case against `O-001`. It
  loses on four of the six criteria. It gives `M-001` a content dependency on `M-002`'s
  heading text, which is a dependency in the wrong direction: the tool would have to know
  the document in order to render it, and a heading reworded for readability would silently
  drop its anchor because the map key no longer matches. It scores lower on impact surface,
  lower on reuse leverage, and worse on operability, and it converts `C-010` from satisfied
  to unsatisfiable without a tool change.

- Tradeoffs accepted:

  - The source gains notation it does not carry today. `F-009` establishes that the file has
    no links and no blockquotes at present, so the blockquote callout and the brace attribute
    are both newly introduced to this document even though both are ordinary Markdown. This
    is the tradeoff `C-011` measures, and `SGC-2` already rules that where `C-011` and
    `C-002` conflict, `C-002` governs and the count is reported rather than enforced.
  - The brace attribute is markup on an otherwise-prose line. It was chosen over a
    separate-line form precisely because `AC-013` counts lines: 21 anchor identifiers carried
    on separate lines would raise the count by 21, whereas carried as a suffix they raise it
    by zero lines. Whether a prose line with a trailing attribute is classified as markup is
    the counting rule's decision, which `T-012` owns; this design states the input, not the
    rule.
  - The chapter numbering already present in the source headings becomes load-bearing: the
    chapter label, the navigation number, and the section nesting all derive from it. It was
    already load-bearing for the reader, who is told to see section 5b, so this makes an
    existing dependency explicit rather than creating one.
  - The published page's design system moves into the renderer as a fixed shell. Changing the
    palette or the type scale becomes a tool change rather than a file edit. This is accepted
    because the shell is presentational scaffolding under `SD-002` and carries no authored
    content except the masthead strapline and the footer sentence, both of which stay
    content.

### 5.4 Decisions

| ID | Decision | Architecture-significant | Record |
|---|---|---|---|
| D-001 | Non-derivable published-form values are authored in the source, on the line they belong to, in one brace attribute construct; the renderer holds no document-content map. Follows `O-001` | Yes | ADR D-001, status Proposed |
| D-002 | A level-2 heading whose ordinal prefix is a digit followed by a letter renders as a level-3 subsection of that digit's chapter and is excluded from the navigation index; a plain-digit prefix opens a chapter. Follows `O-001` | No | Inline; reproduces `F-028` and keeps the section set at 9 |
| D-003 | A callout is authored as a blockquote whose leading bolded run becomes its tag, with the brace attribute supplying a variant where one exists. Follows `O-001` | No | Inline; reuses the bolded lead-in of `F-008` and supplies the tag text of `F-007` |
| D-004 | Comment marking inside a code sample is decided by a lexical rule keyed to the fence's info string and aware of quoting: a comment marker opens a comment only when it is at line start or preceded by whitespace and is not inside a quoted run on that line. Follows `O-001` | No | Inline; the quote-awareness clause exists to reproduce `F-013` |
| D-005 | A chain diagram is authored as a fenced block whose info string names it, with the gate-marked token written in bold inside the block. Follows `O-001` | No | Inline; the accessibility label is derived by default, pending `Q-001` |
| D-006 | The page shell — title, style block, font stylesheet link, masthead frame, and footer frame — is held verbatim by the renderer; only the masthead strapline and the footer's authored sentence are content. Follows `O-001` | No | Inline; classified as presentational scaffolding under `SD-002` |
| D-007 | Determinism is established at the renderer's own input and output boundary — explicit encoding, an explicit newline policy, and document-order emission of every collected sequence — and defended at checkout by pinning the two handbook paths against line-ending translation. Follows `O-001` | Yes | ADR D-007, status Proposed |
| D-008 | The drift check is a step inside the existing tests job, landing under the two platform-suffixed tests check names, rather than a new job or a proof script. Follows `O-001` | Yes | ADR D-008, status Proposed |
| D-009 | Check mode renders into memory, reads the committed published file as bytes, compares, and writes nothing to the working tree on either outcome. Follows `O-001` | No | Inline; required by `C-014` and `S-011` |
| D-010 | The renderer fails the build on a duplicate anchor identifier and on an internal link to an identifier no heading declares. Follows `O-001` | No | Inline; converts the internal link graph of `F-003` from a review obligation into a build-time one |

## API and Data Model Impact

API changes:

- `M-001` introduces one command-line surface with two modes: a default mode that writes the
  published file, and a check mode that writes nothing and reports a verdict through its exit
  status. `S-011` and `C-013` fix the check mode's failure output: it carries the
  regeneration command as a runnable string. `A-003` records that one command form is assumed
  to serve both platforms; `R-003` and the `T-004` evidence settle it.
- `M-002` gains an authoring grammar, which is the contract a contributor writes against.
- `M-003` loses its hand-editing contract entirely.
- `M-004` gains one step. No job identifier, job name, or rendered check name changes, which
  `C-005` makes non-negotiable and `F-016` makes mechanically enforced.

Contract compatibility notes for `M-002`, the source handbook (`D-001`):

- Current shape: a Markdown document with headings, tables, fenced code blocks with info
  strings, bolded lead-in paragraphs, and no links, blockquotes, or attributes (`F-009`).
- Target shape: the same document, plus a trailing brace attribute on the 21 headings that
  carry an anchor and the callouts that carry a variant, plus blockquote callouts, plus an
  info string on the two chain fences.
- Compatibility approach: purely additive at the notation level. Every existing construct
  keeps its current meaning; a heading with no attribute still renders, taking a derived
  slug, and a paragraph that is not a blockquote still renders as a paragraph. A contributor
  who writes plain Markdown produces a valid, if unadorned, page.
- Coexistence period: from the first reconciled commit until every heading that must expose a
  stable identifier carries one. In practice this is a single commit, because the
  reconciliation and the notation land together.
- Retirement condition: none. The attribute form is the steady state, not a transitional
  device.
- Rollback position: the source is a valid Markdown document with or without the attributes.
  Reverting the tool and deleting the attributes leaves a readable document; the published
  file returns to its pre-change committed content by revert, and `M-006`'s docstring
  correction and `M-007`'s instruction revert with it.

Contract compatibility notes for `M-003`, the published handbook (`D-001`, `D-007`):

- Current shape: a hand-authored file, editable in place, whose content is authoritative for
  the two committed test assertions in `F-020` and `F-021`.
- Target shape: a generated file, byte-determined by `M-002` and by `M-001`'s fixed shell,
  carrying a generated-do-not-edit banner at the top of the rendered page (`C-009`).
- Compatibility approach: the file stays committed and stays at its current path, so both
  committed test assertions keep reading it from the working tree and `X-007` holds. `C-008`
  makes every asserted string non-droppable: the dependency-footprint paragraph of `F-022` is
  non-droppable because `F-021` asserts it, and the unresolved-import troubleshooting row of
  `F-023` is non-droppable because it states a fact about tool behaviour and `SGC-1` resolves
  fact-stating published-form wording as merged. Both are absent from `M-002` today and both
  merge into it.
- Coexistence period: none. The file is hand-authored before the change and generated after
  it, with no interval in which both are true.
- Retirement condition: not applicable; nothing is retired.
- Rollback position: revert the commit. The published file returns to its committed
  pre-change bytes, `M-004`'s step disappears with it, and no runtime, gate-decision, or
  approval surface was touched (`C-007`), so nothing else needs unwinding.

Contract compatibility notes for the check-name contract:

- `M-004`'s step lands under the rendered check names the tests job already produces
  (`F-015`). Branch protection binds to those names and they do not change, so no
  branch-protection edit is required and none is proposed. `F-019` establishes that the
  ubuntu leg is required from the first run and the windows leg is advisory until the flip;
  `D-008` records the consequence explicitly rather than assuming the flip.

Schema or migration changes: there is no data model and no persisted schema. The one
migration is of the published handbook's own bytes, and it runs in one direction only, from
hand-authored to generated. It is reversible by revert, because the pre-change content stays
in version history and nothing outside the repository consumes the file. During the
transition there is no reader whose behaviour splits: both committed test assertions read the
file the same way before and after, and the only reader whose behaviour changes is a human
who has been editing the published file directly, which is what the banner in `C-009` and the
documentation in `S-014` exist to tell. The one deviation from a clean forward migration is
`A-007`: if the committed file's terminal bytes do not match the renderer's newline policy,
that file's final bytes are rewritten once, which `Q-005` routes for acceptance.

## Reusable Components and Reuse Rationale

| Capability | Candidate | Outcome | Rationale |
|---|---|---|---|
| Rendering a Markdown document to the published page | A Markdown implementation in the standard library | none-found | The search looked at the standard library's own module set, which carries a markup writer for none of the Markdown dialects, and at the repository's declared dependency set, which declares exactly one runtime dependency and none for tooling (`F-032`). `C-003` forbids adding one, so a purpose-built converter over the constructs this document actually uses is licensed |
| Rendering a Markdown document to the published page | A third-party Markdown library | rejected | It would satisfy the capability well, but `C-003` is a hard constraint traced to `S-006` and to the published dependency statement of `F-022`; adopting one would make that published statement false and stop the change being additive. Rejected on `C-003`, and `R-011` of the supplied plan already names the reopening it would force |
| The published page's design system and frame | The committed published file's title, style block, font link, masthead frame, and footer frame | reuse-as-is | `F-029` establishes the shell exists and is self-contained apart from the font link. Lifting it verbatim into `M-001` reproduces the palette, the type scale, and the light and dark tokens exactly, which is what makes byte identity attainable at all rather than approachable |
| The stable anchor identifier set | The 21 identifiers `docs/user-guide.html` already declares | reuse-as-is | `F-002` and `F-003` establish the set and its closure. `C-002` requires exactly this set to survive, so it is carried forward unchanged into the source rather than regenerated |
| The aside notation the source already uses | The bolded lead-in paragraph form, present 20 times (`F-008`) | reuse-extended | The lead-in already marks the aside and already carries emphasis; extending it with a blockquote container and reading the bolded run as the tag reuses what a contributor already writes and supplies the tag text `F-007` shows is missing, without inventing a second emphasis convention |
| Byte comparison and a nonzero verdict | The standard library's file reading and process exit status | reuse-as-is | `C-003` permits it, and the comparison is a byte-sequence equality test over two in-memory values; nothing richer is required and nothing richer would be more reliable |
| Cross-platform execution of a repository check | The existing tests job and its two-entry platform matrix (`F-015`) | reuse-extended | The job already provisions the interpreter, already installs the package, and already runs on both platforms under the two check names branch protection binds to. One added step reuses all of it. `C-005` and `F-016` make this the only shape available, and `F-033` establishes that adding a step to this job disturbs no positional step extraction in the parity test |
| Discovery discipline for the checked surface | The workflow's discovery job, which enumerates a file set at run time (`F-014`) | rejected | Enumeration is unsuitable here because the drift check has exactly one known build output, so a discovery expression would enumerate a single fixed path and add a job the `C-005` topology forbids. `S-019` asks for a step over a known build output rather than a curated file list, and naming one build output is not a curated list; `F-017`'s assertion is unaffected because neither handbook path matches the patterns it scans for |
| Proof-script reporting for the determinism evidence | The proof-script convention under the framework runtime directory and its passing-summary contract | rejected | Two reasons make it unsuitable. Its verdict reaches branch protection only through the fan-in checks, which `F-019` establishes are advisory until the flip, so a drift check expressed this way would run without being able to block a merge, defeating `S-012`. Its reporting shape is a summary line parsed by a wrapper, whereas the drift check's contract is an exit status plus a runnable fix command (`C-013`) |
| Checkout-time line-ending stability | An existing line-ending attributes file at the repository root | none-found | The search looked at the repository root for an attributes file and found none (`F-026`). `C-004` requires byte identity on both platforms and `A-002` cannot be established from supplied context, so `M-005` is licensed as new structure |
| Carrying a value that must not render as prose | The source's existing constructs: headings, tables, fenced blocks with info strings, and bolded runs (`F-009`, `F-011`) | rejected | Each was examined. A heading cannot carry a hidden value because everything on a heading line is its text. A table cannot, because the value belongs to one line rather than to a row set. A fence info string can, and is used for the chain construct in `D-005`. A bolded run can, and is used for the callout tag in `D-003`. None can carry a per-heading identifier that must not be read as prose, which is what licenses the one new construct in `D-001` |

The two `rejected` rows for the discovery job and the proof-script convention, and the
`none-found` row for the attributes file, are what license the only new structure in this
design: `M-001`, `M-005`, and the brace attribute. Without them each would be new structure
proposed over an unexamined existing component.

## Operational Considerations

- Logging and observability updates: `M-001`'s check mode is the only new observable. Its
  failure output reaches the workflow run log through the tests job's step output
  (`M-004`, `C-013`), and it names the differing position rather than printing the file, so a
  contributor learns where the divergence is without the log carrying a thousand lines of
  markup. Its success path stays silent enough not to bury the unit-test output that shares
  the same check name.

- Error handling strategy: `M-001` distinguishes three failures, because a single nonzero
  exit for all of them would leave a contributor guessing. A source file that violates the
  notation grammar — a duplicate identifier or an internal link to an identifier no heading
  declares (`D-010`) — fails the render itself, naming the source line. A missing published
  file fails the check as a mismatch, because an absent build output is the strongest form of
  staleness. A byte mismatch fails with the regeneration command (`C-013`). Check mode
  writes nothing on any of the three (`C-014`, `D-009`).

- Security considerations: the change's security surface is narrow and is narrower after it
  than before. `M-001` reads two fixed paths and writes one, executes no subprocess, opens no
  network connection, and accepts no input beyond a mode flag, which `C-014` fixes as a
  design property rather than an implementation habit. `M-004` inherits the workflow's
  existing read-only repository permission and its no-secrets posture unchanged, and adds no
  step that fetches anything; `C-012` is untouched because the step introduces neither a
  colour-suppression variable nor a failure-masking key. The one genuine exposure risk is
  content, not code: the reconciliation merges published-form wording into the source, and
  wording written for a published page may name internal detail the source document was not
  intended to carry. `R-009` carries it and routes the judgement to the reviewer who reads
  each merged item against the file that carried it, which is the only control that can
  decide a content question. No secret, credential, or restricted detail appears in either
  handbook file today (`F-022`, `F-023` are both public tool behaviour), and none is
  introduced.

- Performance considerations: `C-004` is the only quality attribute this change is bound to;
  no performance attribute is stated in the approved scope or the supplied request, and none
  is invented here. The operational cost that does exist is runner time: `M-004` adds one
  step to a job that already provisions an interpreter and installs a package, so the added
  cost is one process over two files on each of two legs, which is negligible against the
  job's existing work and adds no runner to the matrix.

- Deployment and operability impact: `M-005` is the only change outside the repository's own
  source that alters how the repository behaves at checkout, and it is speculative until
  `A-002` is settled. The operability change contributors will actually feel is the one
  `R-010` names: anyone who has been editing `M-003` directly loses their edit at the next
  regeneration and is failed by the drift check. `C-009` puts the notice where they will see
  it, and `S-014` puts it where they will look afterwards.

## Delivery Plan

### Sequencing Constraints

| ID | Constraint | Modules | Prerequisites | Reason | Binds |
|---|---|---|---|---|---|
| P-001 | The anchor identifier baseline is enumerated from the committed published file and fixed before any source notation is chosen | M-003 | none | The notation must reproduce a known set; choosing the construct first would fix what it can carry before knowing what it must carry, and `F-004` means nothing about the set can be inferred | T-009, T-010 |
| P-002 | The source notation is defined and closed over every affordance, every baseline identifier, and every item the resolution list marks merged, before the renderer is built | M-002, M-003 | P-001 | The renderer's grammar is the notation; building first would fix the grammar by implementation accident rather than by decision, and every later consumer binds to it. The inventory and its resolutions are prerequisites of that closure, because a notation closed over content that has not been resolved is closed over the wrong set, which is `A-004`. The counting rule, the count, and the authoring walkthrough are all stated or taken against this notation, so none of them can be settled before it is | T-001, T-006, T-007, T-010, T-012, T-013, T-014, T-003, T-002 |
| P-003 | The encoding, the newline policy, the emission-ordering rule, and the checkout attribute decision are fixed before the renderer produces its first output | M-001, M-005 | P-002 | Byte identity cannot be retrofitted onto an output whose input and output boundary was left to defaults; `C-004` is a property of the boundary, not of the content | T-003, T-002 |
| P-004 | The renderer reproduces the committed published file byte for byte from the reconciled source before any consumer binds to the byte comparison | M-001, M-003 | P-003 | The check mode's whole contract is byte equality; a comparison against an output that has never matched has nothing to decide | T-002, T-005 |
| P-005 | Byte identity is proven on both matrix platforms immediately after the renderer first matches, and before the drift step is wired into the workflow | M-001, M-005 | P-004 | Line-ending and encoding divergence is a property of the platform and the checkout, not of the check. Wiring first would make a platform defect present as a continuous-integration defect on a required check name, with the wrong surface blamed and the wrong fix attempted | T-002, T-004, T-016 |
| P-006 | Check mode exists, compares in memory, and writes nothing before the workflow invokes it | M-001 | P-004 | A workflow step invoking a mode that writes would mutate a runner checkout mid-run and could turn a passing comparison into a false pass on the next step | T-015, T-016 |
| P-007 | A demonstration that a sentence added directly to the published file is absent after regeneration is recorded before the change closes | M-003 | P-004 | `AC-002` is the criterion that evidences the source-of-truth property itself, and no other check reaches it: the byte comparison and the platform evidence both compare a regeneration against a commit, neither of which exercises a discarded direct edit | T-019, T-022 |
| P-008 | The drift step is added inside the existing tests job, with all six job identifiers and all four stable check names unchanged, and the workflow parity test still passing | M-004, M-011 | P-005, P-006 | Branch protection binds to rendered check names and `F-016` asserts the job identifier set; a new job detaches the first and fails the second in the same commit | T-016 |
| P-009 | The generated-do-not-edit banner is emitted by the renderer rather than added to the published file, before the page verdict is taken | M-001, M-003 | P-004 | A banner not emitted by the renderer is erased by the next regeneration, so a page verdict taken on a hand-added banner would certify something that cannot persist | T-017, T-011 |
| P-010 | The contributor instruction naming the regeneration command, and the closure record that hands that command to the dependent ticket, are published only after the command form has run unmodified on both platforms | M-007, M-006 | P-005 | Documenting a command form before it is proven on both platforms documents a guess, and `AC-003` requires the string a contributor runs unmodified; the closure record carries the same string to the ticket that depends on it | T-018, T-021 |
| P-011 | Every string a committed test asserts in the published file is confirmed present in the regenerated output before the reconciliation is accepted | M-003, M-008 | P-004 | `C-008` makes those strings a hard boundary on what the reconciliation may drop, and confirming after acceptance would mean reopening a decision the Scope Gate already reserved | T-005, T-008, T-020 |

These are structural constraints, not tasks. `Binds` names the supplied plan's tasks each
constraint governs; the planner owns their decomposition and this design creates no task
identifier. `P-005` is the constraint the Planning Gate's third condition asks for: the
cross-platform probe sits immediately after the renderer first matches, not only in the
formal evidence that `T-004` produces later. `P-007` carries the fourth condition; `Q-002`
routes the question of which task executes it, because assigning it is the planner's call and
not this agent's.

### Test Strategy Focus Areas

For `omn-qa`:

- Byte identity under repetition in one environment and across both platform legs of a single
  workflow run, with the line-ending question probed explicitly rather than inferred from a
  passing comparison (`C-004`, `A-002`, `P-005`).
- The discarded-direct-edit demonstration: a sentence inserted into the published file and
  absent after regeneration (`AC-002`, `P-007`).
- Check-mode purity: the working tree is unchanged after both a passing and a failing check,
  including the absence of any temporary file beside the output (`C-014`, `D-009`).
- Failure-output usability: the regeneration command appears in the run log as one string a
  contributor can copy and run unmodified on the platform whose leg failed (`C-013`,
  `A-003`).
- The committed-assertion boundary: the four stable check names, the workflow filename, and
  the dependency-distribution name are all present in the regenerated published file
  (`C-008`, `F-020`, `F-021`).
- Workflow topology: the job identifier set, the four rendered check names, and the parity
  test's positional step extraction are all unchanged after the step is added (`C-005`,
  `F-016`, `F-033`).
- Grammar failure paths: a duplicate anchor identifier and an internal link to an undeclared
  identifier each fail the render with the source line named (`D-010`).
- The anchor baseline: all 21 identifiers of Appendix B resolve in the regenerated page to
  the section carrying the same material (`C-002`, `AC-008`).

### Rollout and Rollback

- Rollout: the sequencing constraints govern the order, with `P-008` gated on both `P-005`
  and `P-006`. The reconciled source, the regenerated published file, the renderer, the
  workflow step, and the attributes file land as one change set, because a published file
  regenerated without the step in place would be unguarded, and a step in place without a
  matching published file would fail the required ubuntu check on its first run.
- Rollback: revert the change set. `M-003` returns to its committed pre-change bytes, the
  drift step disappears with the workflow file, `M-005` disappears with it, and the two
  committed test assertions keep passing throughout because neither depends on how the file
  was produced. Nothing in `C-007`'s forbidden surface set is involved, so no state needs
  unwinding and no follow-up cleanup exists. The rollback position for each contract change
  is stated in section 6.

## Risks and Mitigations

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | structural | The delivery revision of the published file declares an anchor identifier absent from the baseline enumerated for this design (`A-001`) | A dropped anchor passes the page verdict and breaks a link a reader already uses, with the anchor criterion satisfied against an incomplete comparison | low | M-003, D-001 | `P-001` fixes the enumeration method rather than the list, so it is re-run against the delivery revision and the two sets compared | omn-tech-lead |
| R-002 | operability | The windows runner presents the committed published file with translated line endings (`A-002`) | The windows leg of the byte comparison fails permanently regardless of renderer correctness, and the failure reads as a renderer defect | high | M-005, D-007 | `P-005` probes both platforms before the step is wired, so the divergence surfaces as a platform finding rather than as a continuous-integration failure; `M-005` pins the two handbook paths against checkout translation | omn-qa |
| R-003 | contract | The drift step is placed where its verdict reaches only an advisory check name | The check runs, shows red, and cannot block a merge, so a stale published file still reaches the default branch and `S-012` is defeated | medium | M-004, D-008 | `D-008` places the step in the tests job, whose ubuntu leg `F-019` establishes as required from the first run; the windows leg is stated as advisory rather than assumed to have flipped | omn-tech-lead |
| R-004 | delivery | The reconciliation produces an item that the fixed notation cannot express (`A-004`) | The notation reopens after implementation started, and the markup count and the authoring walkthrough are both taken against a moving target | medium | M-002, D-001 | `P-002` closes the notation over the affordance set, the baseline, and the resolution list before the renderer is built, and the notation's four constructs cover prose, aside, diagram, and sample, which is the full shape inventory `F-007` to `F-012` establish | omn-product-owner |
| R-005 | contract | The reconciliation drops a string a committed test asserts in the published file | The unit-test suite fails on the required check, or the reconciliation reopens as a scope change after implementation started | medium | M-003, M-008 | `C-008` makes such an item non-droppable and `P-011` confirms every one present before the reconciliation is accepted; the two known items are named in section 6 | omn-product-owner |
| R-006 | structural | A later change renames a heading's anchor attribute and its internal links together, so the build-time link check passes while an external link breaks (`A-008`) | An identifier readers link to disappears with no mechanical signal, and `X-006` keeps the check that would catch it out of scope | medium | M-003, D-001 | The baseline in Appendix B is recorded as fixed, and the page verdict compares against it; `Q-004` routes to the product owner whether the boundary funds a mechanical assertion of the set, under the revisit condition `X-006` already carries | omn-tech-lead |
| R-007 | operability | The drift step and the unit-test step are ordered so that a failure in either prevents the other from reporting | A contributor fixes one surface, pushes, and discovers the other, paying two round trips for one commit | medium | M-004, D-008 | `D-008` places the drift step after the suite and marks it to run regardless of the suite's outcome, so both surfaces report in one run; the job still fails, and no failure-masking key is introduced, which `C-012` requires | omn-dev-1-implement |
| R-008 | migration | The committed published file's terminal bytes do not match the renderer's newline policy (`A-007`) | The first regeneration differs from the commit in its final bytes, and `AC-001` cannot pass without rewriting the target once | medium | M-003, D-007 | `P-004` requires the match before any consumer binds to the comparison, so the discrepancy surfaces at the earliest point it can; `Q-005` routes acceptance of a one-time rewrite | omn-dev-1-implement |
| R-009 | security | A merged published-form sentence names internal detail the source document was not intended to carry | Content exposure widens without a review having judged it, in a file with a wider audience than the page it came from | low | M-002, P-011 | Each merged item is read against the file that carried it before the change, as part of the review that `P-011` sequences | omn-dev-2-reviewer |
| R-010 | operability | A contributor who has been editing the published file directly continues to do so | Their edit is lost at the next regeneration and their change is failed by a required check, with no explanation unless the page and the documentation give one | high | M-003, D-008 | `C-009` puts the notice at the top of the rendered page and `P-009` makes the renderer emit it, so it cannot be lost; `P-010` puts the same statement in contributor documentation | omn-documentation |
| R-011 | delivery | The chain diagrams' accessibility labels are ruled authored content after the notation is fixed (`A-005`) | The chain construct gains a field after the renderer is built, and the two published labels change in the interim | low | M-002, D-005 | `Q-001` routes the ruling to the owner who decides published wording, and `D-005`'s construct accepts an optional label without a grammar change, so either ruling is absorbed | omn-product-owner |
| R-012 | structural | The purpose-built converter mis-parses a construct the source already uses, and the error surfaces as a byte difference somewhere unrelated | The byte comparison reports a mismatch whose cause is not where it is reported, and debugging is proportional to the file rather than to the defect | medium | M-001, P-004 | `P-004` requires a full byte match against the committed file before anything binds to the comparison, which makes every parsing defect surface at once and against a known-good target rather than incrementally | omn-dev-1-implement |

## Estimate and Confidence

- Overall: `L` (confidence: low).

- Breakdown:

  - `P-001`, `P-002`: `M` together. The enumeration is bounded and complete; the notation must
    close over six affordances and 21 identifiers, which is analysis rather than construction.
  - `P-003`, `P-004`: `L` together. Reproducing 1033 lines of an existing hand-authored page
    byte for byte from a converter written for the occasion is the single largest piece of
    structural work in the change, and `R-012` is its characteristic failure.
  - `P-005`: `S`, but with the highest uncertainty per unit of work in the change, because
    `A-002` is unconfirmed and `R-002` is the most likely way the change fails.
  - `P-006`, `P-009`: `S` each. Both are bounded behaviours of a component that already
    exists by that point.
  - `P-007`: `XS`. One insertion, one regeneration, one observation.
  - `P-008`: `S`. One step inside an existing job, constrained by two committed assertions
    that make the acceptable shape unambiguous.
  - `P-010`, `P-011`: `S` each. Both are confirmations over a fixed inventory.

- Scope assumptions: the estimate covers the eleven sequencing constraints above and assumes
  `A-002` through `A-007` hold. It excludes the reconciliation's own content decisions, which
  the Scope Gate reserved to the product owner and which this design constrains but does not
  size. It excludes the raw-markup counting rule and the validation strategy, both owned by
  `omn-qa`. It assumes the published page's shell is lifted verbatim rather than rewritten,
  per `D-006`.

- Uncertainty drivers: confidence is `low` because the estimate depends on the speculative
  impact `M-005` and on the unconfirmed assumptions `A-002`, `A-005`, and `A-007`. The
  dominant driver is byte-exact reproduction of an existing hand-authored artifact: the
  distance between a converter that produces a correct-looking page and one that produces the
  committed bytes is not knowable from the supplied context, and `R-012` is the risk that
  carries it. The secondary driver is `A-002`, which is binary in effect: it either costs
  nothing or it fails one required leg until `M-005` exists.

## Open Decisions and Escalations

| ID | Question | Blocking | Owner | Affects | Consequence |
|---|---|---|---|---|---|
| Q-001 | Are the two chain diagrams' accessibility labels authored content to merge into the source, or derived presentation to regenerate from the token list? | No | omn-product-owner | M-002, D-005, R-011 | Ruled derived, the labels are regenerated and their current wording changes, which is a published-wording change the Scope Gate reserved. Ruled authored, the chain construct carries an optional label field and the source gains one more thing a contributor may write |
| Q-002 | Which executing task carries the demonstration that a direct edit to the published file does not survive regeneration? | No | planner | P-007 | `AC-002` currently has a sequencing constraint and no executing task. Assigning it to the demonstration task groups it with the drift demonstration; assigning it to the validation strategy groups it with the criteria coverage. This agent records the constraint and declines to create the task, because task identifiers belong to the planner |
| Q-003 | Does any consumer outside this repository link to the published file's anchors in a form this change cannot enumerate? | No | omn-product-owner | M-003, R-006 | If none, the obligation is exactly the 21 identifiers of Appendix B and `AC-008` bounds it completely. If some exist, the obligation is wider than the criterion states and the criterion under-specifies the change |
| Q-004 | Does the boundary fund a mechanical assertion that the enumerated anchor identifiers are present in the published file, or does the recorded exclusion keep it out? | No | omn-product-owner | M-003, R-006 | The exclusion currently keeps it out and accepts review instead. Funding it would close `R-006` mechanically at the cost of one assertion; leaving it out keeps the accepted gap the closure record must name |
| Q-005 | If the committed published file's terminal bytes do not match the renderer's newline policy, is a one-time rewrite of that file's final bytes accepted within this change? | No | omn-tech-lead | M-003, D-007, R-008 | Accepted, the first regeneration writes the file once and every regeneration after it matches. Refused, the renderer's newline policy is bent to the committed file's existing terminal bytes, which fixes a determinism decision to an accident of the current commit |
| Q-006 | Is the windows tests check expected to be required by the time this change lands, or does the drift check block on the ubuntu leg alone at delivery? | No | omn-tech-lead | M-004, D-008, R-003 | Required, the drift check blocks on both legs and cross-platform staleness is caught at merge. Still advisory, the drift check blocks on the ubuntu leg only, and a windows-specific divergence shows red without blocking until the flip. This design assumes the latter and does not depend on the flip |

Decision records `D-001`, `D-007`, and `D-008` remain at status `Proposed` and require
Design Gate acceptance before `P-002`, `P-003`, and `P-008` respectively begin. No open
question is blocking, so the package status is `complete`: every one of the six changes what
is recorded rather than what is selected, and none of them can change the selected option.

## Sign-off

- Architect: omn-architect (producing role; excluded from accepting this package)
- Tech Lead: omn-tech-lead (accepting owner for the Design Gate)
- QA: omn-qa (verification implications, sections 9 and 10)

Design Gate owners are `omn-architect` and `omn-tech-lead` per the workflow gate matrix.
Under the producer exclusion rule, acceptance rests with `omn-tech-lead`, because the
architecture role produced this package. Lines are left unsigned by the producing agent.

Handoff. This package and its three decision records go to `omn-orchestrator`,
`omn-tech-lead`, and `omn-dev-1-implement`. Requiring Design Gate approval before execution:
`D-001`, `D-007`, `D-008`, and with them the sequencing constraints `P-002`, `P-003`, and
`P-008`. Requiring product confirmation: `Q-001`, `Q-003`, `Q-004`. Requiring tech-lead
confirmation: `Q-005`, `Q-006`. Requiring planner action: `Q-002`. No implementation work was
performed, no production code, test, migration, script, or configuration was written, and no
external system was accessed.

## Appendix A: Traceability Closure Evidence

Forward closure. All 38 statements map. `S-001`, `S-002`, `S-003` map to `F-001`, `F-022`,
`F-023` and to the reconciliation boundary in section 6. `S-004`, `S-037` map to the first
architectural objective and to `C-001`. `S-005`, `S-020`, `S-025` map to `C-004` and `D-007`.
`S-006`, `S-028` map to `C-003` and to the two Markdown-library survey rows. `S-007`,
`S-008`, `S-009`, `S-017` map to `C-008` and to section 6's non-droppable items. `S-010`,
`S-024`, `S-032`, `S-038` map to `D-001` through `D-006` and to `C-010`. `S-011`, `S-026` map
to `D-009` and `C-014`. `S-012`, `S-019`, `S-035`, `S-036` map to `D-008`, `C-005`, `C-006`.
`S-013`, `S-016` map to `C-009` and `P-009`. `S-014` maps to `P-010` and `M-007`. `S-015`
maps to `C-013` and `P-008`. `S-018` maps to `C-007` and to the four `no-change-verified`
modules. `S-021` maps to `M-008` through `M-011`. `S-022` maps to this package's own writing
form. `S-023` maps to `A-003` and `P-010`. `S-027` maps to `A-003` and `Q-006`. `S-029` maps
to `F-014`, `F-015`, `F-019`. `S-030`, `S-031` map to `C-002` and Appendix B. `S-033` maps to
`C-008`. `S-034` maps to `M-006`.

Backward closure. Every module traces to a fact or an assumption in its Basis column. Every
decision traces to `O-001` through the selection. Every option traces to the constraint set
`C-001` to `C-015`, and the two eliminated options each name the hard constraint that
eliminated them.

Lateral closure. Every risk attaches to an existing module, decision, or plan step. Every
plan step names existing modules and existing prerequisites, and the prerequisite graph is
acyclic. Every decision record corresponds to a decision marked architecture-significant in
section 5.4, and the metadata block lists exactly those three. The one speculative impact,
`M-005`, has `R-002`. The approach-changing assumptions `A-001` through `A-008` each have a
matching risk: `A-001` to `R-001`, `A-002` to `R-002`, `A-003` to `R-003`, `A-004` to
`R-004`, `A-005` to `R-011`, `A-006` to `R-010`, `A-007` to `R-008`, `A-008` to `R-006`.

Register integrity. No claim about the current system appears anywhere in this package
without an `F-nnn` or `A-nnn` reference. The fact register carries 33 entries, each citing
the file read that establishes it; the assumption register carries 8, each stating why it is
needed, what changes if it is false, and who can confirm it. The two registers are disjoint.

Plan coverage. Every one of the supplied plan's 22 tasks is reached by at least one
sequencing constraint through its `Binds` column. The reconciliation tasks reach `P-002`
because the notation must close over the resolved content, not over the content as it stands
before resolution; the counting-rule, count, and walkthrough tasks reach `P-002` because each
is stated or taken against the defined notation; and the closure task reaches `P-010` because
the regeneration command it hands to the dependent ticket is the command that step proves.
Reaching a constraint is an ordering obligation only; the planner owns what each task does
and when it is executed.

## Appendix B: Anchor Identifier Baseline

Method. Every attribute declaring an element identifier in the committed `docs/user-guide.html`
was enumerated, and separately every internal link target in the same file. The two sets were
compared. The result is 21 declared identifiers and 21 link targets forming an equal set
(`F-002`, `F-003`). The enumeration was taken from the committed file itself, not from any
list supplied to this agent. This set is fixed and must survive regeneration; `C-002` and
`AC-008` are satisfied only if every row below resolves, after the change, to the section
carrying the same material.

Chapter-level identifiers, 9, each declared on a chapter section element:

| Identifier | Chapter | Heading it carries | Navigation label | Label differs from heading |
|---|---|---|---|---|
| `model` | 1 | The mental model | The mental model | no |
| `install` | 2 | Installation | Installation | no |
| `work` | 3 | Two ways to work | Two ways to work | no |
| `flows` | 4 | The flows: pick by what you're trying to do | The flows, by intent | yes |
| `run` | 5 | Driving a run | Driving a run | no |
| `ownership` | 6 | What's yours and what's the framework's | Yours vs. the framework's | yes |
| `health` | 7 | Keeping the installation healthy | Keeping it healthy | yes |
| `trouble` | 8 | Troubleshooting | Troubleshooting | no |
| `custom` | 9 | Customizing the framework for your team | Customizing | yes |

In-chapter identifiers, 12, each declared on a level-3 heading:

| Identifier | Parent chapter | Heading it carries |
|---|---|---|
| `flow-implement` | 4 | 4.1, implement a feature |
| `flow-bugfix` | 4 | 4.2, fix a bug |
| `flow-refactor` | 4 | 4.3, refactor |
| `flow-investigate` | 4 | 4.4, investigate and research |
| `flow-review` | 4 | 4.5, review a pull request |
| `flow-release` | 4 | 4.6, release |
| `flow-quality-scan` | 4 | 4.7, scan for code junk |
| `rework` | 5 | When changes are requested: the rework loop |
| `fix-comments` | 5 | One-command review-comment loop |
| `update` | 5 | One-command change-request loop |
| `run-e2e` | 5 | One command from ticket to pull request, any provider |
| `live-view` | 5 | Watching a run live in the terminal |

Derivability. Not one of the 21 is the slug of its own heading text under any common slug
algorithm, which is the finding that decides the notation question (`F-004`). Three
counter-examples suffice: "Troubleshooting" would slug to a nine-letter word, not to
`trouble`; "The mental model" would slug to three hyphenated words, not to `model`; and the
heading numbered 4.1 would slug to a string beginning with its own digits, not to
`flow-implement`. Four of the nine navigation labels also differ from their heading text
(`F-005`), so the navigation index carries a second set of non-derivable values alongside the
first. Both sets are what `D-001` moves into the source.

Consequence for the notation. Because the identifiers are not derivable and the internal link
graph is closed over them (`F-003`), a derivation-only renderer would break 21 anchors and
21 internal links in one commit, which is why `O-004` is eliminated on `C-002` rather than
scored. Because the same is true of four navigation labels and all 14 callout tags
(`F-007`), the same construct serves all three, which is what makes `D-001` one decision
rather than three.
