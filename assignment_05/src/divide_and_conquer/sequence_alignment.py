"""Smith-Waterman local sequence alignment via dynamic programming.

Smith-Waterman finds the best-matching *substrings* of two sequences (as
opposed to Needleman-Wunsch, which aligns the sequences end to end). It is
the right choice for this assignment's genome data: `testAgainst` is a
different-but-similar snippet to `genomeSnippet`, and the task is to find
where in `targetGenome` it best matches, not to force an alignment across
their full, mismatched lengths.

DP structure (CLRS-style):
1. Optimal substructure: the best local alignment ending at positions
   (i, j) either extends the best alignment ending at (i-1, j-1) with a
   match/mismatch of a[i-1] and b[j-1], extends the alignment ending at
   (i-1, j) or (i, j-1) with a gap, or -- unique to the *local* alignment
   problem -- starts over from score 0 right here, if every other option
   would make the score negative.
2. Recurrence: H[i][j] = max(0, H[i-1][j-1] + score(a[i-1], b[j-1]),
   H[i-1][j] + gap, H[i][j-1] + gap), with H[i][0] = H[0][j] = 0.
3. Bottom-up computation: fill the (len(a)+1) x (len(b)+1) table H in
   row-major order; each cell only depends on already-computed neighbors.
4. Constructing the solution: the best local alignment's score is the
   maximum value anywhere in H. Backtrace from that cell, at each step
   re-deriving which of the three recurrence cases produced the current
   cell's value, until a cell with value 0 is reached.

See docs/sequence_alignment.md for the scoring scheme, a hand-verified test
case, and the results of running this on the assignment's genome data.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Alignment:
    """The result of a Smith-Waterman local alignment.

    aligned_a and aligned_b are the two aligned substrings, the same length,
    with '-' marking a gap. start_a/end_a (and start_b/end_b) are the
    half-open [start, end) index ranges in the original sequences that the
    alignment covers.
    """

    score: int
    aligned_a: str
    aligned_b: str
    start_a: int
    end_a: int
    start_b: int
    end_b: int


def smith_waterman(a: str, b: str, match: int = 3, mismatch: int = -3, gap: int = -2) -> Alignment:
    """Find the best local alignment between a and b.

    Default scoring (match=+3, mismatch=-3, gap=-2 per gap step) matches
    the worked example on Wikipedia's Smith-Waterman page, used as a unit
    test in tests/test_sequence_alignment.py.
    """
    n, m = len(a), len(b)
    h = [[0] * (m + 1) for _ in range(n + 1)]

    best_score = 0
    best_i, best_j = 0, 0

    for i in range(1, n + 1):
        row = h[i]
        prev_row = h[i - 1]
        a_char = a[i - 1]
        for j in range(1, m + 1):
            diag = prev_row[j - 1] + (match if a_char == b[j - 1] else mismatch)
            up = prev_row[j] + gap
            left = row[j - 1] + gap
            cell = max(0, diag, up, left)
            row[j] = cell
            if cell > best_score:
                best_score = cell
                best_i, best_j = i, j

    aligned_a: list[str] = []
    aligned_b: list[str] = []
    i, j = best_i, best_j
    while i > 0 and j > 0 and h[i][j] > 0:
        current = h[i][j]
        diag = h[i - 1][j - 1] + (match if a[i - 1] == b[j - 1] else mismatch)
        if current == diag:
            aligned_a.append(a[i - 1])
            aligned_b.append(b[j - 1])
            i -= 1
            j -= 1
        elif current == h[i - 1][j] + gap:
            aligned_a.append(a[i - 1])
            aligned_b.append("-")
            i -= 1
        else:
            aligned_a.append("-")
            aligned_b.append(b[j - 1])
            j -= 1

    aligned_a.reverse()
    aligned_b.reverse()

    return Alignment(
        score=best_score,
        aligned_a="".join(aligned_a),
        aligned_b="".join(aligned_b),
        start_a=i,
        end_a=best_i,
        start_b=j,
        end_b=best_j,
    )
