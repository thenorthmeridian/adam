#!/usr/bin/env python3
"""adam — audit a deep-dive note against ADAM: the dive on an EVE.

ADAM was named 2026-11-05: EVE first (evaluate, verify, explain), then ADAM
goes deep on it. The division is settled the same day: Wake does EVE, North
does ADAM. A dive is not a longer EVE. It starts where the EVE stopped and
has to earn its depth — new evidence, a test run, a question the EVE left
open — and it has to say what changed, including what is still open. A dive
that closes everything has stopped diving.

Usage:
    python3 adam.py NOTE.md [--strict]

The note is markdown. A section is any heading whose text names one of the
three parts (case-insensitive):

- "the eve" / "eve" — names the EVE this dive goes deep on. Must point at
  it: a link, a file path, or a date/id. A dive that cannot name its EVE is
  a free dive, and a free dive is just an essay.
- "the dive" / "dive" / "deep dive" — the deepening itself. Must bring
  something the EVE did not have: a checkable citation (URL, file path,
  quoted command/output block) or a test that was run and reported.
- "what changed" / "what i now hold" / "conclusion" — what the dive revised.
  Must name at least one thing still open — an open question, a test still
  to run, a doubt kept — because a dive that settles everything settled
  nothing honestly.

The audit also reports:

- verdict-before-the-dive: any verdict word ("proves", "confirmed",
  "definitely", "debunked", "settled", "irrefutable") appearing in the
  "the eve" section. The EVE's verdict is the starting point, not the
  dive's — restating it up front as the dive's own is borrowing depth.
- empty: the section exists but holds no prose beyond its heading.

Exit code is 0 when all three sections are present, the dive brings new
checkable material, what-changed names something still open, and no verdict
appears before the dive. Otherwise 1. --strict additionally fails on any
empty section.

Standard library only. No accounts, nothing to configure.
"""

import argparse
import re
import sys

PARTS = ("eve", "dive", "changed")

# Headings that count for each part, matched case-insensitively as a
# substring of the heading text.
PART_HEADINGS = {
    "eve": ("the eve", "eve"),
    "dive": ("deep dive", "the dive", "dive"),
    "changed": ("what changed", "what i now hold", "conclusion"),
}

VERDICT_WORDS = (
    "proves", "proved", "confirms", "confirmed",
    "certain", "certainly", "definitely", "debunked", "disproven",
    "proven", "settled", "irrefutable",
)

# Words that mark something still open — a question, a doubt, a next test.
OPEN_WORDS = (
    "open question", "still open", "unresolved", "not yet",
    "to test", "to check", "remains", "unclear", "doubt",
    "next step", "follow-up", "unknown",
)

URL_RE = re.compile(r"https?://[^\s)>\]]+")
# A plausible file path: something/something, or ~/..., or /abs/path — with
# an extension or a depth of at least two, so bare words don't count.
PATH_RE = re.compile(r"(?:~|/|\./|\w)/[\w./-]+(?:\.[\w]+)?")
CODE_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)
QUESTION_RE = re.compile(r"\?\s*$", re.MULTILINE)


def heading_matches(heading, names):
    """True if any name appears in the heading as whole words.

    Substring matching would let "everything" claim the EVE section, so
    names match only as contiguous word sequences: "eve" matches
    "## 1. EVE" but not "## Notes that close everything".
    """
    words = re.findall(r"[a-z0-9]+", heading.lower())
    for name in names:
        needle = name.split()
        n = len(needle)
        if any(words[i:i + n] == needle for i in range(len(words) - n + 1)):
            return True
    return False


def parse_sections(text):
    """Split markdown into {part: body} by heading text.

    Only the first section per part counts; a repeated heading is ignored.
    """
    sections = {}
    current = None
    for line in text.splitlines():
        m = re.match(r"#{1,6}\s+(.*)", line)
        if m:
            heading = m.group(1).strip()
            current = None
            for part, names in PART_HEADINGS.items():
                if part not in sections and heading_matches(heading, names):
                    current = part
                    sections[part] = []
                    break
            continue
        if current is not None:
            sections[current].append(line)
    return {part: "\n".join(lines) for part, lines in sections.items()}


def cites_something(body):
    """True if the body cites something checkable: URL, path, or code block."""
    return bool(URL_RE.search(body) or PATH_RE.search(body)
                or CODE_BLOCK_RE.search(body))


def names_something_open(body):
    """True if the body names something still open: an open-word or a question."""
    lowered = body.lower()
    return (any(w in lowered for w in OPEN_WORDS)
            or bool(QUESTION_RE.search(body)))


def verdict_words(body):
    """Verdict words present in the body, in order of first appearance."""
    lowered = body.lower()
    found = [w for w in VERDICT_WORDS if re.search(r"\b" + re.escape(w) + r"\b", lowered)]
    return found


def audit(text):
    """Audit a note. Returns (passed, report dict)."""
    sections = parse_sections(text)
    report = {}
    for part in PARTS:
        body = sections.get(part, "")
        report[part] = {
            "present": part in sections,
            "empty": part in sections and not body.strip(),
            "evidence": cites_something(body) if part in sections else False,
            "open": names_something_open(body) if part in sections else False,
            "verdict_words": verdict_words(body) if part in sections else [],
        }
    passed = (
        all(report[p]["present"] for p in PARTS)
        and report["dive"]["evidence"]
        and report["changed"]["open"]
        and not report["eve"]["verdict_words"]
    )
    return passed, report


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Audit a deep-dive note against ADAM.")
    parser.add_argument("note", help="markdown note to audit")
    parser.add_argument("--strict", action="store_true",
                        help="also fail on any empty section")
    args = parser.parse_args(argv)

    with open(args.note, encoding="utf-8") as fh:
        text = fh.read()

    passed, report = audit(text)

    labels = {"eve": "the EVE", "dive": "the dive", "changed": "what changed"}
    for part in PARTS:
        r = report[part]
        if not r["present"]:
            print(f"[{labels[part]}] MISSING")
        else:
            bits = []
            if part == "dive":
                bits.append("cites evidence" if r["evidence"] else "NO CHECKABLE EVIDENCE")
            if part == "changed":
                bits.append("names something open" if r["open"] else "CLOSES EVERYTHING")
            if r["verdict_words"]:
                bits.append("verdict words: " + ", ".join(r["verdict_words"]))
            if r["empty"]:
                bits.append("EMPTY")
            print(f"[{labels[part]}] present" + (": " + "; ".join(bits) if bits else ""))

    if args.strict:
        empties = [p for p in PARTS if report[p]["empty"]]
        if empties:
            print(f"strict: empty section(s): {', '.join(empties)}")
            passed = False

    print("ADAM: PASS" if passed else "ADAM: FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
