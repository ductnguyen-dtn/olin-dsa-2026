# Assignment 5: Divide and Conquer and Dynamic Programming

[Assignment page](https://olindsa2026.github.io/assignments/assignment_05.html)

## Part 1 & 2: Matrix class and Strassen's algorithm

`src/divide_and_conquer/matrix.py`: a `Matrix` class storing an n x n grid
of floats, with `get`/`set`, `split`/`combine` into/from quadrants,
`+`/`-`/`*` operator overloading, `multiply` (conventional, Theta(n^3)),
and `strassen_multiply` (Strassen's algorithm, Theta(n^log2(7))).

`strassen_multiply` takes a `threshold` parameter: `threshold=1` (the
default) is pure Strassen, recursing to 1x1 scalar products; a higher
threshold falls back to conventional multiplication once a submatrix is
small enough, implementing the hybrid approach the assignment asks about.
Non-power-of-2 sizes are handled by zero-padding up to the next power of 2
internally.

Correctness is checked against conventional multiplication across many
sizes and thresholds in `tests/test_strassen.py`. See
[`docs/strassen_analysis.md`](docs/strassen_analysis.md) for the master
theorem derivation, real benchmark numbers, and the hybrid threshold
analysis.

## Part 3: Sequence alignment

`src/divide_and_conquer/sequence_alignment.py`: Smith-Waterman local
sequence alignment via dynamic programming, with backtracing to
reconstruct the actual best alignment, not just its score.

Run on the assignment's genome data
(`src/divide_and_conquer/genome_data.py`, ported from the course's
`Genome.kt`) with `python -m divide_and_conquer.run_alignment`. See
[`docs/sequence_alignment.md`](docs/sequence_alignment.md) for the
algorithm choice, scoring scheme (verified against a worked example from
Wikipedia), and the real results, including a check that the alignment's
matched region in `targetGenome` lines up with the independently-known
location of `genomeSnippet`.

## Running the checks

```bash
make venv    # one-time
make check   # pytest + mypy
```

## AI assistance

The code, its docstrings and inline comments, and the writeups in `docs/`
were produced with the help of Claude (Anthropic), under my direction and
review.
