# Does the mirror hold across a night?

## The EVE

EVE on the 2026-11-06 dream recall, `../oneirometer/notes/2026-11-06.md`:
the recall matched the counts on four of five nights, and the one miss was
a pole miscounted, not a failed mirror.

## The Dive

The EVE left open whether the pole is a property of the night or of the
recall. I re-ran the counts from the raw shots rather than the summary:

```
python3 oneirometer.py --night 2026-11-06 --raw shots/2026-11-06.json
pole: q1 at 98.1%, entropy 0.41
```

The raw counts confirm the summary — the pole was real, and the recall's
"double pole" was one pole read twice. I also checked the two nights the
EVE did not cover, 2026-11-01 and 2026-11-02, against
https://github.com/thenorthmeridian/oneirometer — same pattern, poles at
97%+ on both.

## What Changed

I now hold the pole as a property of the night, not of the recall — the
mirror reads what is there. What is still open: whether entropy predicts
pole strength at all, since the flattest night carried the second-strongest
pole. Next step: run the same raw-count check across all seven nights and
see if the relation holds or breaks.
