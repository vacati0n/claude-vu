#!/usr/bin/env python3
"""Render the operator handbook: docs/USER-GUIDE.md -> docs/user-guide.html.

The Markdown file is the source of record. The HTML file is a build output and
is never authored directly. Regenerate with:

    python tools/render_user_guide.py

Check mode re-renders in memory, compares against the committed HTML byte for
byte, writes nothing, and exits nonzero on a mismatch:

    python tools/render_user_guide.py --check

Determinism: every read and write states its encoding, the input newline form is
normalised before parsing, the output newline is fixed to LF by the writer
rather than delegated to the platform, every collected sequence is emitted in
the source's document order, and no value taken from the environment (build
time, tool version, host name, computed path) reaches the output.

Standard library only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_REL = "docs/USER-GUIDE.md"
OUTPUT_REL = "docs/user-guide.html"
RENDER_COMMAND = "python tools/render_user_guide.py"
CHECK_COMMAND = "python tools/render_user_guide.py --check"

FONT_STYLESHEET = (
    "https://fonts.googleapis.com/css2?family=Spectral:wght@500;600"
    "&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400"
    "&family=IBM+Plex+Mono:wght@400;500&display=swap"
)

STYLE = """\n  :root {
    --paper: #FAFBF9;
    --ink: #1F2E33;
    --muted: #5C6B6E;
    --accent: #0E7268;
    --accent-ink: #0A5A52;
    --warn: #A05A17;
    --line: #DCE4E0;
    --card: #F0F5F2;
    --code-bg: #EAF1EE;
    --chip-bg: #E2ECE8;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --paper: #101A1D;
      --ink: #E3EBE9;
      --muted: #94A6A4;
      --accent: #48BFB2;
      --accent-ink: #6FD3C8;
      --warn: #D99A55;
      --line: #233236;
      --card: #152225;
      --code-bg: #0C1619;
      --chip-bg: #1B2C2E;
    }
  }
  :root[data-theme="dark"] {
    --paper: #101A1D;
    --ink: #E3EBE9;
    --muted: #94A6A4;
    --accent: #48BFB2;
    --accent-ink: #6FD3C8;
    --warn: #D99A55;
    --line: #233236;
    --card: #152225;
    --code-bg: #0C1619;
    --chip-bg: #1B2C2E;
  }
  * { box-sizing: border-box; }
  body {
    background: var(--paper);
    color: var(--ink);
    font-family: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
    font-size: 1rem;
    line-height: 1.65;
    margin: 0;
    padding: 0 1.25rem 5rem;
  }
  main { max-width: 47rem; margin: 0 auto; }
  h1, h2, h3 {
    font-family: "Spectral", Georgia, serif;
    font-weight: 600;
    line-height: 1.2;
    text-wrap: balance;
    margin: 0;
  }
  h1 { font-size: 2.4rem; letter-spacing: -0.01em; }
  h2 { font-size: 1.5rem; margin: 0 0 0.75rem; }
  h3 { font-size: 1.1rem; margin: 1.75rem 0 0.5rem; }
  p { margin: 0.75rem 0; max-width: 66ch; }
  a { color: var(--accent-ink); text-decoration-color: var(--line); text-underline-offset: 3px; }
  a:focus-visible, button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  code, pre {
    font-family: "IBM Plex Mono", ui-monospace, Consolas, monospace;
    font-size: 0.875em;
  }
  code { background: var(--code-bg); padding: 0.1em 0.35em; border-radius: 3px; }
  pre {
    background: var(--code-bg);
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 0.9rem 1.1rem;
    overflow-x: auto;
    line-height: 1.55;
    margin: 1rem 0;
  }
  pre code { background: none; padding: 0; }
  .comment { color: var(--muted); }

  /* masthead */
  header { padding: 3.5rem 0 0; }
  .kicker {
    font-family: "IBM Plex Mono", monospace;
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent-ink);
    margin-bottom: 0.9rem;
  }
  .lede { font-size: 1.08rem; color: var(--muted); max-width: 62ch; margin-top: 1rem; }
  .lede strong { color: var(--ink); font-weight: 600; }

  /* the chain */
  .chain {
    display: flex; flex-wrap: wrap; align-items: center; gap: 0.4rem 0.5rem;
    margin: 1.75rem 0 0; padding: 1rem 1.1rem;
    background: var(--card); border: 1px solid var(--line); border-radius: 8px;
  }
  .chain span {
    font-family: "IBM Plex Mono", monospace; font-size: 0.78rem;
    background: var(--chip-bg); border: 1px solid var(--line);
    padding: 0.22em 0.6em; border-radius: 999px; white-space: nowrap;
  }
  .chain b { color: var(--accent); font-weight: 400; }
  .chain .gate { border-color: var(--accent); color: var(--accent-ink); background: transparent; }

  /* toc */
  nav {
    margin: 2.25rem 0 0; padding: 0; display: grid;
    grid-template-columns: repeat(auto-fill, minmax(13rem, 1fr)); gap: 0.15rem 1.5rem;
  }
  nav a {
    font-size: 0.9rem; text-decoration: none; color: var(--ink);
    padding: 0.3rem 0; border-bottom: 1px solid var(--line); display: block;
  }
  nav a:hover { color: var(--accent-ink); }
  nav .n { font-family: "IBM Plex Mono", monospace; font-size: 0.72rem; color: var(--muted); margin-right: 0.5em; }

  section { margin-top: 3.5rem; }
  .eyebrow {
    font-family: "IBM Plex Mono", monospace; font-size: 0.72rem;
    letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted);
    margin: 0 0 0.4rem;
  }
  .eyebrow::before { content: ""; display: inline-block; width: 1.6rem; height: 1px;
    background: var(--accent); vertical-align: middle; margin-right: 0.6rem; }

  /* tables */
  .tbl { overflow-x: auto; margin: 1rem 0; border: 1px solid var(--line); border-radius: 6px; }
  table { border-collapse: collapse; width: 100%; font-size: 0.9rem; }
  th {
    font-family: "IBM Plex Mono", monospace; font-size: 0.7rem; font-weight: 500;
    letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted);
    text-align: left; padding: 0.55rem 0.9rem; border-bottom: 1px solid var(--line);
    background: var(--card);
  }
  td { padding: 0.55rem 0.9rem; border-bottom: 1px solid var(--line); vertical-align: top; }
  tr:last-child td { border-bottom: none; }
  td:first-child { white-space: nowrap; }
  .num td:first-child { font-family: "IBM Plex Mono", monospace; font-variant-numeric: tabular-nums; }

  /* callouts */
  .callout {
    border: 1px solid var(--line); border-left: 3px solid var(--accent);
    background: var(--card); border-radius: 0 6px 6px 0;
    padding: 0.8rem 1.1rem; margin: 1.25rem 0; font-size: 0.95rem;
  }
  .callout.yours { border-left-color: var(--warn); }
  .callout .tag {
    font-family: "IBM Plex Mono", monospace; font-size: 0.7rem;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--accent-ink);
    display: block; margin-bottom: 0.25rem;
  }
  .callout.yours .tag { color: var(--warn); }

  ul, ol { padding-left: 1.3rem; max-width: 64ch; }
  li { margin: 0.35rem 0; }
  li::marker { color: var(--accent); }

  .steps { counter-reset: step; list-style: none; padding: 0; margin: 1rem 0; }
  .steps li {
    counter-increment: step; position: relative; padding-left: 2.4rem; margin: 0.9rem 0;
  }
  .steps li::before {
    content: counter(step); position: absolute; left: 0; top: 0.05em;
    font-family: "IBM Plex Mono", monospace; font-size: 0.78rem;
    width: 1.6rem; height: 1.6rem; display: flex; align-items: center; justify-content: center;
    border: 1px solid var(--accent); border-radius: 999px; color: var(--accent-ink);
  }

  footer {
    margin-top: 4.5rem; padding-top: 1.25rem; border-top: 1px solid var(--line);
    font-size: 0.85rem; color: var(--muted);
  }
  @media (prefers-reduced-motion: no-preference) {
    html { scroll-behavior: smooth; }
  }
  /* generated-file banner */
  .banner {
    border: 1px solid var(--line); border-left: 3px solid var(--warn);
    background: var(--card); border-radius: 0 6px 6px 0;
    padding: 0.8rem 1.1rem; margin: 2.5rem 0 0; font-size: 0.9rem;
    color: var(--muted);
  }
  .banner code { background: var(--code-bg); }
  .banner .tag {
    font-family: "IBM Plex Mono", monospace; font-size: 0.7rem;
    letter-spacing: 0.12em; text-transform: uppercase; color: var(--warn);
    display: block; margin-bottom: 0.25rem;
  }
"""

# Comment markers per fence info string. A fence whose info string is absent
# from this map carries no comment marking at all.
COMMENT_MARKERS = {
    "bash": "#",
    "sh": "#",
    "shell": "#",
    "console": "#",
    "json": "//",
    "jsonc": "//",
}

CHAIN_INFO = "chain"

ARROW = "→"
MIDDOT = "·"
NEWLINE = "\n"


class SourceError(Exception):
    """The source document violates the authoring grammar."""

    def __init__(self, line_number, message):
        super().__init__("%s:%d: %s" % (SOURCE_REL, line_number, message))
        self.line_number = line_number


# --------------------------------------------------------------------------
# inline rendering
# --------------------------------------------------------------------------

_LINK = re.compile(r"\[([^\]\[]+)\]\((#[A-Za-z0-9][A-Za-z0-9_-]*)\)")
_ATTR = re.compile(r"\s*\{([^{}]*)\}\s*$")
# An anchor identifier or a class name: the same alphabet the link grammar
# accepts, so a value that reaches an `id`, `href` or `class` attribute can
# never carry a quote, a space or an angle bracket.
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def escape(text):
    """Escape text for element content."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def escape_attribute(text):
    """Escape text for a double-quoted attribute value.

    Element-content escaping leaves the quote intact, so a value carrying one
    would close the attribute early. Every value the renderer places in
    attribute position passes through here, not through `escape`.
    """
    return escape(text).replace('"', "&quot;")


def render_inline(text, links=None):
    """Render one run of inline Markdown.

    A code span is atomic and is read before every other construct, so a
    backtick run never has emphasis, a link, or an escape applied inside it.
    """
    out = []
    index = 0
    total = len(text)
    while index < total:
        char = text[index]
        if char == "`":
            close = text.find("`", index + 1)
            if close == -1:
                out.append(escape(char))
                index += 1
                continue
            out.append("<code>" + escape(text[index + 1:close]) + "</code>")
            index = close + 1
            continue
        if char == "[":
            match = _LINK.match(text, index)
            if match:
                target = match.group(2)
                if links is not None:
                    links.append(target[1:])
                out.append('<a href="%s">%s</a>'
                           % (escape_attribute(target),
                              render_inline(match.group(1), links)))
                index = match.end()
                continue
        if text.startswith("**", index):
            close = text.find("**", index + 2)
            if close != -1:
                out.append("<strong>%s</strong>"
                           % render_inline(text[index + 2:close], links))
                index = close + 2
                continue
        if char == "*":
            close = text.find("*", index + 1)
            if close != -1 and close > index + 1:
                out.append("<em>%s</em>"
                           % render_inline(text[index + 1:close], links))
                index = close + 1
                continue
        out.append(escape(char))
        index += 1
    return "".join(out)


def strip_emphasis(text):
    """The plain-text reading of an inline run, for derived labels."""
    plain = re.sub(r"`([^`]*)`", r"\1", text)
    plain = _LINK.sub(r"\1", plain)
    plain = plain.replace("**", "").replace("*", "")
    return plain.strip()


def take_attributes(text, number):
    """Split a trailing brace attribute off a line.

    The construct carries the values the published form needs and the source
    cannot derive: a section's anchor identifier, a navigation label that
    differs from its heading text, and a block variant.

    `number` is the source line the attribute sits on. An anchor identifier or
    a class name outside the identifier alphabet, or a double quote anywhere
    in the braces, fails the render naming that line: each would otherwise
    reach an attribute value and break it silently.
    """
    match = _ATTR.search(text)
    if not match:
        return text.rstrip(), {"classes": []}
    body = match.group(1).strip()
    if '"' in body:
        raise SourceError(
            number, "a brace attribute may not contain a double quote: {%s}"
            % body)
    attrs = {"classes": []}
    for token in body.split():
        if token.startswith("#"):
            if not _IDENTIFIER.match(token[1:]):
                raise SourceError(
                    number, "an anchor identifier must match %s: %r"
                    % (_IDENTIFIER.pattern, token[1:]))
            attrs["id"] = token[1:]
        elif token.startswith("."):
            if not _IDENTIFIER.match(token[1:]):
                raise SourceError(
                    number, "a class name must match %s: %r"
                    % (_IDENTIFIER.pattern, token[1:]))
            attrs["classes"].append(token[1:])
        elif "=" in token:
            key, _, value = token.partition("=")
            attrs[key] = value
        else:
            raise SourceError(
                number, "an unrecognised brace attribute token: %r" % token)
    return text[:match.start()].rstrip(), attrs


# --------------------------------------------------------------------------
# document model
# --------------------------------------------------------------------------


class Paragraph(object):
    kind = "paragraph"

    def __init__(self, text):
        self.text = text


class Heading3(object):
    kind = "heading3"

    def __init__(self, text, anchor):
        self.text = text
        self.anchor = anchor


class ListBlock(object):
    kind = "list"

    def __init__(self, ordered, items, classes):
        self.ordered = ordered
        self.items = items
        self.classes = classes


class TableBlock(object):
    kind = "table"

    def __init__(self, header, rows):
        self.header = header
        self.rows = rows


class CodeBlock(object):
    kind = "code"

    def __init__(self, info, lines):
        self.info = info
        self.lines = lines


class ChainBlock(object):
    kind = "chain"

    def __init__(self, tokens):
        self.tokens = tokens


class CalloutBlock(object):
    kind = "callout"

    def __init__(self, tag, variants, blocks):
        self.tag = tag
        self.variants = variants
        self.blocks = blocks


class Chapter(object):
    def __init__(self, number, title, anchor):
        self.number = number
        self.title = title
        self.anchor = anchor
        self.blocks = []


class Document(object):
    def __init__(self):
        self.title = ""
        self.kicker = ""
        self.lede = []
        self.chapters = []
        self.footer = ""


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------

_H2 = re.compile(r"^##\s+(\d+)([a-z]?)\.\s+(.*)$")
_H3 = re.compile(r"^###\s+(.*)$")
# Any heading-shaped line. One that reaches `read_block` was matched by none
# of the heading forms above (or sits inside a callout, which admits none), so
# it is a grammar failure rather than prose to emit.
_HEADING = re.compile(r"^#{1,6}(?:\s|$)")
_ORDERED_ITEM = re.compile(r"^(\d+)\.\s+(.*)$")
_ATTR_LINE = re.compile(r"^\{([^{}]*)\}$")
_RULE = re.compile(r"^-{3,}$")
_TAG_ONLY = re.compile(r"^\*\*(.+?)\*\*$")


def opens_block(line):
    """Whether this line starts a new block rather than continuing a paragraph."""
    stripped = line.strip()
    if not stripped:
        return True
    if line.startswith("#") or line.startswith("```"):
        return True
    if stripped.startswith(">") or stripped.startswith("|"):
        return True
    if stripped.startswith("- ") or _ORDERED_ITEM.match(stripped):
        return True
    if _ATTR_LINE.match(stripped):
        return True
    return bool(_RULE.match(stripped))


def read_block(lines, index, total, classes, offset):
    """Read one body block. Returns the block (or None) and the next index.

    `offset` is the line number the first line of `lines` carries in the source
    file, so a grammar failure inside a callout still names the source line.
    """
    line = lines[index].rstrip()
    stripped = line.strip()
    number = offset + index

    if _HEADING.match(line):
        raise SourceError(
            number, "a heading the grammar does not recognise: %r" % stripped)

    if line.startswith("```"):
        info = line[3:].strip()
        body = []
        index += 1
        while index < total and not lines[index].strip().startswith("```"):
            body.append(lines[index])
            index += 1
        if index >= total:
            raise SourceError(number, "an unterminated fenced block")
        index += 1
        if info == CHAIN_INFO:
            joined = " ".join(part.strip() for part in body if part.strip())
            return ChainBlock([tok.strip() for tok in joined.split(ARROW)]), index
        return CodeBlock(info, body), index

    if stripped.startswith(">"):
        quoted = []
        while index < total and lines[index].lstrip().startswith(">"):
            rest = lines[index].lstrip()[1:]
            quoted.append(rest[1:] if rest.startswith(" ") else rest)
            index += 1
        first, attrs = take_attributes(quoted[0].strip(), number)
        tag = _TAG_ONLY.match(first.strip())
        if not tag:
            raise SourceError(
                number, "a callout's first line must be its bolded tag alone")
        body = parse_body(quoted[1:], number + 1)
        if not body:
            raise SourceError(number, "a callout carries no body")
        return CalloutBlock(tag.group(1), attrs["classes"], body), index

    if stripped.startswith("|"):
        rows = []
        while index < total and lines[index].lstrip().startswith("|"):
            rows.append(split_row(lines[index]))
            index += 1
        if len(rows) < 3:
            raise SourceError(number, "a table carries no body row")
        return TableBlock(rows[0], rows[2:]), index

    ordered = _ORDERED_ITEM.match(stripped)
    if stripped.startswith("- ") or ordered:
        items, index = read_list(lines, index, total, bool(ordered))
        return ListBlock(bool(ordered), items, classes), index

    buffer = []
    while index < total and lines[index].strip() and not (
            buffer and opens_block(lines[index])):
        buffer.append(lines[index].strip())
        index += 1
    if not buffer:
        return None, index + 1
    return Paragraph(" ".join(buffer)), index


def parse_body(lines, offset):
    """Parse a run of body lines into blocks. No headings, no chapters."""
    blocks = []
    index = 0
    total = len(lines)
    classes = []
    while index < total:
        stripped = lines[index].strip()
        if not stripped:
            index += 1
            continue
        if _RULE.match(stripped):
            index += 1
            continue
        attr_only = _ATTR_LINE.match(stripped)
        if attr_only:
            _, attrs = take_attributes("x {%s}" % attr_only.group(1),
                                       offset + index)
            classes = attrs["classes"]
            index += 1
            continue
        block, index = read_block(lines, index, total, classes, offset)
        classes = []
        if block is not None:
            blocks.append(block)
    return blocks


def parse(source):
    lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    doc = Document()
    index = 0
    total = len(lines)
    chapter = None
    classes = []
    preamble = []
    epilogue = []
    closed = False

    while index < total:
        line = lines[index].rstrip()
        stripped = line.strip()
        number = index + 1

        if not stripped:
            index += 1
            continue

        if line.startswith("# ") and not doc.title:
            doc.title = strip_emphasis(line[2:])
            index += 1
            continue

        if _RULE.match(stripped):
            # A thematic break inside the body closes it: what follows is the
            # document's own footer sentence rather than chapter content.
            if chapter is not None:
                closed = True
            index += 1
            continue

        attr_only = _ATTR_LINE.match(stripped)
        if attr_only:
            _, attrs = take_attributes("x {%s}" % attr_only.group(1), number)
            classes = attrs["classes"]
            index += 1
            continue

        match = _H2.match(line)
        if match:
            text, attrs = take_attributes(match.group(3), number)
            anchor = attrs.get("id")
            if match.group(2):
                if chapter is None:
                    raise SourceError(number, "a lettered section opens no chapter")
                chapter.blocks.append(Heading3(text, anchor))
            else:
                if not anchor:
                    raise SourceError(number, "a chapter heading declares no anchor")
                chapter = Chapter(int(match.group(1)), text, anchor)
                doc.chapters.append(chapter)
            index += 1
            continue

        match = _H3.match(line)
        if match:
            text, attrs = take_attributes(match.group(1), number)
            if chapter is None:
                raise SourceError(number, "a level-3 heading opens no chapter")
            chapter.blocks.append(Heading3(text, attrs.get("id")))
            index += 1
            continue

        block, index = read_block(lines, index, total, classes, 1)
        classes = []
        if block is None:
            continue
        if closed:
            epilogue.append(block)
        elif chapter is None:
            preamble.append(block)
        else:
            chapter.blocks.append(block)

    assign_framing(doc, preamble, epilogue)
    return doc


def assign_framing(doc, preamble, epilogue):
    """The masthead and the footer are the document's own framing prose.

    Before the first chapter: the italic-only paragraph is the strapline the
    masthead shows, and the rest is the lede. After the closing thematic
    break: the paragraph there is the footer sentence.
    """
    texts = [block.text for block in preamble if block.kind == "paragraph"]
    italics = [position for position, text in enumerate(texts)
               if text.startswith("*") and text.endswith("*")
               and not text.startswith("**")]
    if not italics:
        raise SourceError(1, "the document carries no masthead strapline")
    doc.kicker = texts[italics[0]].strip("*").strip()
    doc.lede = [text for position, text in enumerate(texts)
                if position != italics[0]]
    if not doc.lede:
        raise SourceError(1, "the document carries no lede")
    if len(epilogue) != 1 or epilogue[0].kind != "paragraph":
        # Anything else after the closing break would reach no part of the page,
        # so it is a grammar failure rather than content quietly dropped.
        raise SourceError(
            1, "the closing thematic break must be followed by the footer"
               " sentence and nothing else")
    doc.footer = epilogue[0].text.strip("*").strip()


def split_row(line):
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [cell.strip() for cell in body.split("|")]


def read_list(lines, index, total, ordered):
    items = []
    current = []
    while index < total:
        raw = lines[index]
        if not raw.strip():
            look = index + 1
            while look < total and not lines[look].strip():
                look += 1
            if look >= total or not lines[look].startswith((" ", "\t")):
                break
            index += 1
            continue
        stripped = raw.strip()
        opens = (_ORDERED_ITEM.match(stripped) if ordered
                 else stripped.startswith("- "))
        continues = raw.startswith((" ", "\t")) and current
        if opens and not continues:
            if current:
                items.append(" ".join(current))
            body = (_ORDERED_ITEM.match(stripped).group(2) if ordered
                    else stripped[2:])
            current = [body.strip()]
        elif current:
            current.append(stripped)
        else:
            break
        index += 1
    if current:
        items.append(" ".join(current))
    return items, index


# --------------------------------------------------------------------------
# derived presentation
# --------------------------------------------------------------------------

# A dotted number (`4.1`) or a single capital followed by a period (`A.`).
# A bare capital is not an enumerator, or every heading opening with a one-letter
# word would be set off as though it were numbered.
_ENUMERATOR = re.compile(r"^(?:(\d+(?:\.\d+)+)|([A-Z])\.)\s+(.*)$")


def heading3_html(text):
    """A level-3 heading, with a leading enumerator set off from its title."""
    match = _ENUMERATOR.match(text)
    if match:
        return "%s %s %s" % (escape(match.group(1) or match.group(2)), MIDDOT,
                             render_inline(match.group(3)))
    return render_inline(text)


def is_numeric_table(table):
    """A table whose every first body cell is a bare number is marked numeric."""
    if not table.rows:
        return False
    for row in table.rows:
        if not row:
            return False
        if not strip_emphasis(row[0]).strip().isdigit():
            return False
    return True


def chain_label(tokens):
    """The chain's accessibility label, derived from its own token list."""
    plain = [strip_emphasis(token) for token in tokens]
    if len(plain) == 1:
        return "The chain: %s" % plain[0]
    return "The chain: %s, then %s" % (" to ".join(plain[:-1]), plain[-1])


def mark_comments(line, marker):
    """Escape one code line, marking a trailing comment where one opens.

    A marker opens a comment only at line start or after whitespace, and never
    inside a quoted run on that line, so a hash inside a quoted argument value
    stays part of the command.
    """
    if not marker:
        return escape(line)
    quote = ""
    position = 0
    while position < len(line):
        char = line[position]
        if quote:
            if char == quote:
                quote = ""
            position += 1
            continue
        if char in "'\"":
            quote = char
            position += 1
            continue
        if line.startswith(marker, position) and (
                position == 0 or line[position - 1].isspace()):
            return (escape(line[:position])
                    + '<span class="comment">'
                    + escape(line[position:])
                    + "</span>")
        position += 1
    return escape(line)


# --------------------------------------------------------------------------
# emission
# --------------------------------------------------------------------------


def render_blocks(blocks, out, links):
    for block in blocks:
        if block.kind == "paragraph":
            out.append("  <p>%s</p>" % render_inline(block.text, links))
        elif block.kind == "heading3":
            opening = ("<h3>" if not block.anchor
                       else '<h3 id="%s">' % escape_attribute(block.anchor))
            out.append("  %s%s</h3>" % (opening, heading3_html(block.text)))
        elif block.kind == "list":
            tag = "ol" if block.ordered else "ul"
            classes = (' class="%s"' % escape_attribute(" ".join(block.classes))
                       if block.classes else "")
            out.append("  <%s%s>" % (tag, classes))
            for item in block.items:
                out.append("    <li>%s</li>" % render_inline(item, links))
            out.append("  </%s>" % tag)
        elif block.kind == "table":
            classes = ' class="num"' if is_numeric_table(block) else ""
            out.append('  <div class="tbl"><table%s>' % classes)
            out.append("    <tr>%s</tr>" % "".join(
                "<th>%s</th>" % render_inline(cell, links)
                for cell in block.header))
            for row in block.rows:
                out.append("    <tr>%s</tr>" % "".join(
                    "<td>%s</td>" % render_inline(cell, links) for cell in row))
            out.append("  </table></div>")
        elif block.kind == "code":
            marker = COMMENT_MARKERS.get(block.info.lower(), "")
            body = "\n".join(mark_comments(line, marker) for line in block.lines)
            out.append("<pre><code>%s</code></pre>" % body)
        elif block.kind == "chain":
            out.append('  <div class="chain" role="img" aria-label="%s">'
                       % escape_attribute(chain_label(block.tokens)))
            pieces = []
            for token in block.tokens:
                gate = re.match(r"^\*\*(.+?)\*\*$", token.strip())
                if gate:
                    pieces.append('<span class="gate">%s</span>'
                                  % render_inline(gate.group(1), links))
                else:
                    pieces.append("<span>%s</span>" % render_inline(token, links))
            out.append("    " + ("<b>%s</b>" % ARROW).join(pieces))
            out.append("  </div>")
        elif block.kind == "callout":
            classes = " ".join(["callout"] + block.variants)
            out.append('  <div class="%s">' % escape_attribute(classes))
            out.append('    <span class="tag">%s</span>'
                       % render_inline(block.tag, links))
            if len(block.blocks) == 1 and block.blocks[0].kind == "paragraph":
                # A single-paragraph callout is the tag and its sentence; the
                # paragraph wrapper would add a box inside a box.
                out.append("    %s" % render_inline(block.blocks[0].text, links))
            else:
                render_blocks(block.blocks, out, links)
            out.append("  </div>")
        else:  # pragma: no cover - the model defines no other block
            raise SourceError(1, "unknown block kind %r" % block.kind)


def banner_html():
    """The generated-file notice, emitted by the renderer and never authored.

    It carries no build time and no tool version: either would make every
    regeneration differ from the last and destroy the byte comparison the
    drift check rests on.
    """
    return [
        '<div class="banner" role="note">',
        '  <span class="tag">Generated file %s do not edit</span>' % MIDDOT,
        "  This page is generated from <code>%s</code>, where this guide is"
        " versioned. Edit that file, then regenerate with"
        " <code>%s</code>. A change made directly to this file is discarded by"
        " the next regeneration and fails the repository's drift check."
        % (SOURCE_REL, RENDER_COMMAND),
        "</div>",
    ]


def render(source):
    doc = parse(source)
    links = []
    declared = [chapter.anchor for chapter in doc.chapters]
    for chapter in doc.chapters:
        for block in chapter.blocks:
            if block.kind == "heading3" and block.anchor:
                declared.append(block.anchor)
    duplicates = sorted({name for name in declared if declared.count(name) > 1})
    if duplicates:
        raise SourceError(1, "duplicate anchor identifier: %s"
                          % ", ".join(duplicates))

    out = []
    out.append("<title>%s</title>" % escape(doc.title))
    out.append('<link rel="stylesheet" href="%s">'
               % escape_attribute(FONT_STYLESHEET))
    out.append("<style>")
    out.append(STYLE.strip(NEWLINE))
    out.append("</style>")
    out.append("")
    out.append("<main>")
    out.extend(banner_html())
    out.append("<header>")
    out.append('  <p class="kicker">%s</p>' % render_inline(doc.kicker, links))
    out.append("  <h1>%s</h1>" % escape(doc.title))
    for paragraph in doc.lede:
        out.append('  <p class="lede">%s</p>' % render_inline(paragraph, links))
    out.append("")
    out.append('  <nav aria-label="Contents">')
    for chapter in doc.chapters:
        out.append('    <a href="#%s"><span class="n">%d</span>%s</a>'
                   % (escape_attribute(chapter.anchor), chapter.number,
                      render_inline(chapter.title, links)))
    out.append("  </nav>")
    out.append("</header>")

    for chapter in doc.chapters:
        out.append("")
        out.append('<section id="%s">' % escape_attribute(chapter.anchor))
        out.append('  <p class="eyebrow">Chapter %d</p>' % chapter.number)
        out.append("  <h2>%s</h2>" % render_inline(chapter.title, links))
        render_blocks(chapter.blocks, out, links)
        out.append("</section>")

    out.append("")
    out.append("<footer>")
    out.append("  %s" % render_inline(doc.footer, links))
    out.append("</footer>")
    out.append("</main>")

    dangling = sorted({name for name in links if name not in declared})
    if dangling:
        raise SourceError(1, "internal link to an undeclared anchor: %s"
                          % ", ".join(dangling))
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# command line
# --------------------------------------------------------------------------


def read_source(root=None):
    """Read the source. `root` is the repository root; default, this checkout."""
    return (Path(root or REPO_ROOT) / SOURCE_REL).read_text(encoding="utf-8")


def write_output(html, root=None):
    path = Path(root or REPO_ROOT) / OUTPUT_REL
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(html)


def first_difference(left, right):
    limit = min(len(left), len(right))
    for position in range(limit):
        if left[position] != right[position]:
            return position
    if len(left) != len(right):
        return limit
    return -1


def check(html, root=None):
    """Compare the re-rendered page against the committed one. Writes nothing.

    `root` is the repository root holding the pair; by default the checkout
    this script lives in. The test suite passes an isolated copy so that the
    failing outcomes are exercised without touching a tracked file.
    """
    path = Path(root or REPO_ROOT) / OUTPUT_REL
    expected = html.encode("utf-8")
    if not path.exists():
        print("DRIFT: %s is missing; an absent build output is stale."
              % OUTPUT_REL)
        print("Regenerate it with: %s" % RENDER_COMMAND)
        return 1
    with open(path, "rb") as handle:
        committed = handle.read()
    if committed == expected:
        return 0
    position = first_difference(committed, expected)
    line = committed[:position].count(b"\n") + 1
    print("DRIFT: %s does not match a render of %s." % (OUTPUT_REL, SOURCE_REL))
    print("First difference at byte %d (line %d); committed %d bytes, "
          "rendered %d bytes." % (position, line, len(committed), len(expected)))
    print("Regenerate it with: %s" % RENDER_COMMAND)
    return 1


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Render %s into %s." % (SOURCE_REL, OUTPUT_REL))
    parser.add_argument(
        "--check", action="store_true",
        help="re-render in memory and compare against the committed output; "
             "write nothing and exit nonzero on a mismatch")
    parser.add_argument(
        "--root", type=Path, default=None, metavar="DIR",
        help="repository root holding %s and %s; defaults to the checkout "
             "this script lives in" % (SOURCE_REL, OUTPUT_REL))
    args = parser.parse_args(argv)
    try:
        html = render(read_source(args.root))
    except SourceError as error:
        print("ERROR: %s" % error)
        return 2
    if args.check:
        return check(html, args.root)
    write_output(html, args.root)
    print("wrote %s from %s" % (OUTPUT_REL, SOURCE_REL))
    return 0


if __name__ == "__main__":
    sys.exit(main())
