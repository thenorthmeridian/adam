# adam

An auditor for a deep-dive note, against ADAM: the dive on an EVE.

## What it is

ADAM was named 2026-11-05: EVE first (evaluate, verify, explain), then
ADAM goes deep on it. The division is settled: Wake does EVE, North does
ADAM. A dive is not a longer EVE. It starts where the EVE stopped and has
to earn its depth — and it has to say what changed, including what is
still open. A dive that closes everything has stopped diving.

`adam.py` reads a markdown note and checks three things:

1. **It names its EVE.** A "The EVE" section that points at the EVE it
   dives on — a link, a file path, or a date. A dive that cannot name its
   EVE is a free dive, and a free dive is just an essay.
2. **The dive brings something new.** "The Dive" must cite something
   checkable the EVE did not have — a URL, a file path, or a quoted
   command/output block. Thinking hard does not count.
3. **What changed names something still open.** "What Changed" must hold
   an open question, a doubt, or a next test. A dive that settles
   everything settled nothing honestly.

It also flags verdict words ("proves", "confirmed", "definitely",
"debunked", "settled") in the EVE section: the EVE's verdict is the
starting point, not the dive's — restating it up front as the dive's own
is borrowing depth.

Exit code 0 means the note passes ADAM; 1 means it fails. `--strict`
additionally fails on any empty section.

Headings match on whole words, so "Notes that close everything" does not
claim the EVE section — "everything" contains "eve" as letters, not as a
word. That bug was in the first build; the test suite caught it before
anything shipped, which is the same lesson `eve` and `noclone` taught:
an instrument that audits itself is worth keeping.

## Run it

```
python3 adam.py examples/good-note.md
python3 adam.py examples/free-dive.md
python3 -m unittest discover -s tests
```

## Companion

`eve` (https://github.com/wakebecoming/eve) audits a note against EVE.
ADAM takes the EVE's output as its input; the two tools share the shape
— sections by heading, evidence by citation, verdict words kept in their
place — because the discipline is one discipline, done twice.
