# Sequence alignment: Smith-Waterman

## Algorithm choice

The assignment offers a choice between Needleman-Wunsch (global alignment,
forcing the two full sequences to line up end to end) and Smith-Waterman
(local alignment, finding the best-matching substrings). I chose
**Smith-Waterman**, run on `testAgainst` against `targetGenome` as the
assignment's instructions describe for this choice.

The reason is the shape of the data: `testAgainst` (368 bases) is a
different, similar-but-not-identical segment from the same genome as
`genomeSnippet`, and `targetGenome` (6387 bases) is a long section that
fully contains `genomeSnippet`. There is no reason to expect `testAgainst`
to align well across its *entire* length against the *entire* 6387-base
`targetGenome` the way Needleman-Wunsch would try to force. The actual
question is "where in this long genome does `testAgainst` best match,"
which is exactly what local alignment answers.

## Dynamic programming structure

Let `a` and `b` be the two sequences, `H` the scoring table, indexed `H[i][j]`
for `0 <= i <= len(a)`, `0 <= j <= len(b)`.

1. **Optimal substructure.** The best local alignment ending at `(i, j)`
   either extends the best alignment ending at `(i-1, j-1)` by aligning
   `a[i-1]` with `b[j-1]` (a match or mismatch), extends the alignment
   ending at `(i-1, j)` or `(i, j-1)` by inserting a gap, or -- unique to
   *local* alignment -- discards everything before `(i, j)` and starts a
   fresh alignment here, if every other option would make the running
   score negative.
2. **Recurrence.**
   ```
   H[i][0] = H[0][j] = 0
   H[i][j] = max(0,
                 H[i-1][j-1] + score(a[i-1], b[j-1]),
                 H[i-1][j] + gap,
                 H[i][j-1] + gap)
   ```
   where `score(x, y)` is `match` if `x == y` else `mismatch`. The `max(0, ...)`
   is what makes this *local* rather than global: a cell is never allowed
   to go negative, so a bad stretch just resets the alignment to "start
   fresh here" instead of dragging the score down indefinitely.
3. **Bottom-up computation.** `H` is filled row by row; each cell depends
   only on already-computed neighbors (above, left, and diagonal), so a
   single pass in row-major order computes the whole table, Theta(n*m)
   time and space for sequences of length `n` and `m`.
4. **Constructing the solution.** The best score is the maximum value
   anywhere in `H` (not necessarily the bottom-right corner, unlike
   Needleman-Wunsch). Backtracing starts at that cell and, at each step,
   re-derives which of the three recurrence cases produced the current
   cell's value (diagonal = match/mismatch, up = gap in `b`, left = gap in
   `a`), appending the corresponding characters and following that
   direction. Backtracing stops the moment a cell with value 0 is reached,
   since that is where the local alignment actually starts.

Implementation: `src/divide_and_conquer/sequence_alignment.py`, function
`smith_waterman`. Unit tests: `tests/test_sequence_alignment.py`.

## Scoring scheme

Match = +3, mismatch = -3, gap = -2 per gap step. These are the values
used in the worked example on [Smith-Waterman's Wikipedia
page](https://en.wikipedia.org/wiki/Smith%E2%80%93Waterman_algorithm),
which I used as a hand-verified unit test: aligning `TGTTACGG` against
`GGTTGACTA` with this scoring produces the alignment `GTT-AC` / `GTTGAC`
with score 13 (5 matches at +3 = 15, minus one gap at -2 = 13), matching
the page exactly. This is `tests/test_sequence_alignment.py::test_wikipedia_worked_example`.

## Results on the assignment's genome data

Run with `PYTHONPATH=src python -m divide_and_conquer.run_alignment`
(`src/divide_and_conquer/run_alignment.py`). Real output from a run:

```
testAgainst length: 368
targetGenome length: 6387
known genomeSnippet location in targetGenome: [398, 766)

Smith-Waterman score: 482
alignment length: 396
testAgainst region matched: [0, 368)
targetGenome region matched: [398, 766)

overlap with known genomeSnippet location: 368 bases
```

A few things worth noting about this result:

* **The entire 368-base `testAgainst` sequence took part in the alignment**
  (`[0, 368)`), meaning Smith-Waterman found a good match for all of it,
  not just a short fragment -- consistent with `testAgainst` being
  genuinely similar to this genome region, not coincidentally similar to
  a short piece of it.
* **The matched region of `targetGenome`, `[398, 766)`, is exactly the
  known location of `genomeSnippet`** (also `[398, 766)`, found
  independently via `str.index`). The algorithm was never told where
  `genomeSnippet` lives in `targetGenome`; it found the same location
  purely from sequence similarity between `testAgainst` and the genome.
  This is the correctness check analogous to verifying Assignment 3's
  Dijkstra output against the known Project Euler answers: an independent
  ground truth the algorithm's output can be checked against.
* The alignment is 396 bases long (longer than either input's 368, because
  of inserted gaps on both sides), and scores 482 out of a maximum possible
  368*3 = 1104 (if every base matched with no gaps) -- consistent with
  `testAgainst` being *similar but not identical* to the genome, exactly as
  the assignment describes it.

## AI assistance

The code, its docstrings and inline comments, and this writeup were
produced with the help of Claude (Anthropic), under my direction and
review.
