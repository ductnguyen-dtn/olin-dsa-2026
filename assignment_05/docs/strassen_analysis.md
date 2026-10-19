# Strassen's algorithm: complexity analysis and benchmark results

## Master theorem derivation

Conventional matrix multiplication for n x n matrices does a dot product
for each of n^2 output entries, each dot product costing Theta(n), giving
`T(n) = Theta(n^3)`.

Strassen's algorithm instead splits each n x n matrix into four (n/2) x
(n/2) quadrants and computes 7 products of those quadrants (instead of the
8 a direct block-multiplication would need), combining them with a
constant number of (n/2) x (n/2) matrix additions/subtractions. Splitting,
adding, and recombining quadrants is all Theta(n^2) work (just visiting
every entry a constant number of times), so the recurrence is:

```
T(n) = 7 T(n/2) + Theta(n^2)
```

By the master theorem, with `a = 7`, `b = 2`, `f(n) = Theta(n^2)`:
compare `f(n)` to `n^(log_b a) = n^(log2 7) ~= n^2.807`. Since `f(n) = n^2`
grows strictly slower than `n^2.807` (case 1 of the master theorem), the
recursive work dominates and:

```
T(n) = Theta(n^log2(7)) ~= Theta(n^2.807)
```

This is asymptotically better than conventional multiplication's
`Theta(n^3)` -- for large enough n, Strassen does strictly less work. The
benchmark results below show why "for large enough n" is doing a lot of
work in that sentence.

## Implementation

`src/divide_and_conquer/matrix.py`, `Matrix.strassen_multiply`. Handles
non-power-of-2 sizes by zero-padding both operands up to the next power of
2, running Strassen on the padded matrices, then cropping the product back
to the original size -- padding with zeros doesn't change the product's
top-left block, since the padding rows/columns only ever multiply against
zeros. Correctness is verified empirically against conventional
multiplication in `tests/test_strassen.py`, across sizes 1 through 16
including several non-power-of-2 sizes (1, 3, 5, 7) that exercise the
padding path, and across hybrid thresholds 1 through 16 -- this matters
because, per the assignment's warning, several public writeups of
Strassen's algorithm contain errors; this implementation follows the
formulas from the Wikipedia page and checks them against a Theta(n^3)
reference rather than trusting them by inspection alone.

A `threshold` parameter controls the base-case size: `threshold=1` (the
default) is "pure" Strassen, recursing all the way to 1x1 scalar products.
Raising `threshold` makes the function fall back to conventional
multiplication once a submatrix is small enough -- the hybrid approach
described below.

## Benchmark: conventional vs. pure Strassen

Real run, `python -m divide_and_conquer.matrix_benchmark`
(`benchmark_data/algorithm_results.csv`, 3 trials per size, means shown):

| n | conventional | pure Strassen (threshold=1) | Strassen / conventional |
|---|---|---|---|
| 2 | 0.000004s | 0.000032s | 7.6x slower |
| 4 | 0.000004s | 0.000177s | 42.7x slower |
| 8 | 0.000019s | 0.001226s | 64.4x slower |
| 16 | 0.000097s | 0.007015s | 72.3x slower |
| 32 | 0.000759s | 0.052502s | 69.2x slower |
| 64 | 0.005770s | 0.371842s | 64.4x slower |
| 128 | 0.045326s | 2.653141s | 58.5x slower |

Pure Strassen is dramatically slower than conventional multiplication at
every size tested here, by roughly 60-70x once the sizes are large enough
to stabilize. This is exactly the outcome the assignment hints at
("Strassen does not reliably outperform conventional"). The reason is
constant-factor overhead: pure Strassen recurses all the way down to 1x1
scalar products, and in a pure-Python implementation, each level of
recursion pays for several submatrix additions/subtractions (each
allocating new lists), several recursive function calls, and eventually a
huge number of 1x1 "multiplications" that each cost far more in Python
function-call and list-allocation overhead than the single multiply
operation they perform. The asymptotic Theta(n^2.807) vs. Theta(n^3)
advantage is real, but it only wins once n is large enough that the
*growth rate* difference outweighs this constant-factor gap -- and that
crossover point is far beyond what plain nested Python loops can reach in
reasonable time (recursing pure Strassen to n=128 already takes ~2.65
seconds; doubling n roughly multiplies pure Strassen's time by
2^2.807 ~= 7x, while conventional's time only grows by 2^3 = 8x, so the two
would eventually converge, but at sizes far too large to benchmark here
without a much faster per-element implementation, e.g. using numpy arrays
for the base case instead of Python lists).

## Hybrid analysis: finding the optimal threshold

Real run, threshold sweep at a fixed n=128 (`benchmark_data/threshold_results.csv`,
3 trials per threshold, means shown):

| threshold | runtime | speedup vs. threshold=1 |
|---|---|---|
| 1 (pure Strassen) | 2.6972s | 1.0x |
| 2 | 0.6496s | 4.2x |
| 4 | 0.2255s | 12.0x |
| 8 | 0.1161s | 23.2x |
| 16 | 0.0691s | 39.0x |
| 32 | 0.0522s | 51.7x |
| 64 | 0.0460s | 58.6x |
| 128 (= conventional, no recursion at all) | 0.0452s | 59.7x |

Runtime decreases monotonically as the threshold increases, all the way
up to `threshold = n` (at which point `strassen_multiply` never actually
recurses, and degenerates to calling conventional multiplication once).
**The apparent optimal switch-over size, for this pure-Python
implementation at this matrix size, is to not use Strassen's recursion at
all** -- every additional level of recursion costs more in Python overhead
than it saves in arithmetic operations. This matches the algorithm
comparison table above: there is no n in the tested range (up to 128)
where Strassen's recursion pays for itself.

This is a realistic conclusion, not a failure of the implementation:
production numerical libraries that do use Strassen (e.g. in BLAS
implementations) apply it only at matrix sizes in the thousands, with
highly optimized, vectorized base cases -- never recursing anywhere close
to 1x1, for exactly the constant-factor reasons observed here. A pure
Python, list-based implementation makes that constant-factor gap far more
visible than it would be in a lower-level language.

## AI assistance

The code, its docstrings and inline comments, and this writeup were
produced with the help of Claude (Anthropic), under my direction and
review.
