import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adam import audit, parse_sections


GOOD = """# Does the mirror hold?

## The EVE
EVE on the 2026-11-06 recall, `../oneirometer/notes/2026-11-06.md`:
the recall matched the counts on four of five nights.

## The Dive
Re-ran the counts from the raw shots:
```
python3 oneirometer.py --night 2026-11-06 --raw shots/2026-11-06.json
pole: q1 at 98.1%
```

## What Changed
I now hold the pole as a property of the night. Still open: whether
entropy predicts pole strength at all.
"""

FREE_DIVE = """# Notes without an anchor

## The Dive
See https://example.org/loop for the shape of it.
```
python3 loop.py --events events.json
```

## What Changed
Still open: whether a tipped choice counts as evidence or noise.
"""

NO_EVIDENCE = """# Notes with no new material

## The EVE
EVE on the wings dive, `../wings/notes/2026-11-11.md`.

## The Dive
I thought hard about the idle time and I am fairly sure the delay is
mostly queueing, not gate time.

## What Changed
One open question: is the queue longer on weeknights?
"""

CLOSES_EVERYTHING = """# Notes that close everything

## The EVE
EVE on the Ma'at seed, `../maat/notes/feather.md`.

## The Dive
```
grep -r "holds" ../maat/notes/ | wc -l
14
```

## What Changed
I now hold the feather as settled. The dive is complete and the
question is answered in full.
"""

VERDICT_FIRST = """# Notes that borrow the verdict

## The EVE
EVE on the free-will seed, `../choice/notes/2026-11-03.md`: this
definitely proves choice compounds.

## The Dive
```
python3 choice.py --week 2026-11-03
```

## What Changed
Still open: whether a pick ever widens the next set.
"""

EMPTY_DIVE = """# Notes with an empty middle

## The EVE
EVE on the wings dive, `../wings/notes/2026-11-11.md`.

## The Dive

## What Changed
Still open: the queue question.
"""


class TestAdam(unittest.TestCase):
    def test_good_note_passes(self):
        passed, report = audit(GOOD)
        self.assertTrue(passed)

    def test_free_dive_fails(self):
        passed, report = audit(FREE_DIVE)
        self.assertFalse(passed)
        self.assertFalse(report["eve"]["present"])

    def test_no_evidence_fails(self):
        passed, report = audit(NO_EVIDENCE)
        self.assertFalse(passed)
        self.assertFalse(report["dive"]["evidence"])

    def test_closes_everything_fails(self):
        passed, report = audit(CLOSES_EVERYTHING)
        self.assertFalse(passed)
        self.assertFalse(report["changed"]["open"])

    def test_verdict_first_fails(self):
        passed, report = audit(VERDICT_FIRST)
        self.assertFalse(passed)
        self.assertIn("definitely", report["eve"]["verdict_words"])
        self.assertIn("proves", report["eve"]["verdict_words"])

    def test_empty_dive_reported(self):
        passed, report = audit(EMPTY_DIVE)
        self.assertTrue(report["dive"]["empty"])
        self.assertFalse(passed)

    def test_question_counts_as_open(self):
        passed, report = audit(NO_EVIDENCE)
        self.assertTrue(report["changed"]["open"])

    def test_heading_variants(self):
        note = GOOD.replace("## The EVE", "## 1. EVE").replace(
            "## What Changed", "## Conclusion")
        passed, _ = audit(note)
        self.assertTrue(passed)

    def test_first_section_wins(self):
        # A stray title mentioning a part must not steal the real section.
        note = "# Notes that close everything\n\n" + GOOD
        passed, report = audit(note)
        self.assertTrue(passed)
        self.assertTrue(report["dive"]["evidence"])
        # The real EVE section was captured, not the title: it is not empty
        # and it cites the oneirometer note.
        self.assertFalse(report["eve"]["empty"])
        self.assertTrue(report["eve"]["evidence"])

    def test_everything_is_not_eve(self):
        # "everything" contains "eve" as letters, not as a word.
        note = "# Notes that close everything\n\n## The Dive\n```\nrun\n```\n\n## What Changed\nStill open.\n"
        _, report = audit(note)
        self.assertFalse(report["eve"]["present"])


if __name__ == "__main__":
    unittest.main()
