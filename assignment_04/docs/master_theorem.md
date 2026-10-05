# Master theorem worksheet

Worksheet: [MIT 6.046J, Handout 9](https://courses.csail.mit.edu/6.046/spring02/handouts/master.pdf).
Worked below against the general method, then cross-checked against the
[official solutions](https://courses.csail.mit.edu/6.046/spring02/handouts/mastersol.pdf)
after deriving each one independently (every answer here matches, with the
reasoning spelled out rather than just quoted).

**The method**, for a recurrence of the form T(n) = aT(n/b) + f(n), a ≥ 1,
b > 1: compute n^(log_b a), the cost of the recursion tree if every level did
equal work, and compare it to f(n), the actual cost of the work done outside
the recursive calls at the top level.

* **Case 1**, f(n) grows polynomially *slower* than n^(log_b a): the leaves
  dominate. T(n) = Θ(n^(log_b a)).
* **Case 2**, f(n) = Θ(n^(log_b a) · logᵏ n) for some k ≥ 0: every level costs
  about the same. T(n) = Θ(n^(log_b a) · log^(k+1) n). (k = 0 is the standard
  textbook case 2; k > 0 is the natural extension used in a few problems
  below, which several of the problems below need.)
* **Case 3**, f(n) grows polynomially *faster* than n^(log_b a), **and** the
  regularity condition a·f(n/b) ≤ c·f(n) holds for some c < 1 and large n:
  the top level dominates. T(n) = Θ(f(n)).
* If none of these match (not of the aT(n/b)+f(n) form at all, or f(n) sits in
  a gap between cases, or case 3's growth holds but regularity fails), the
  master theorem does not apply, and a different tool is needed: unrolling the
  recurrence directly, a recursion tree, or (for uneven splits like
  T(n/2) + T(n/4)) the more general Akra-Bazzi method.

n^(log_b a) is computed as `log(a) / log(b)` in the exponent; where it comes
out to a recognizable value (like log₂3 ≈ 1.585, not a round number) it's left
as `n^(log_b a)` to match how the solutions are conventionally written.

| # | Recurrence | log_b(a) vs. f(n) | Case | T(n) |
|---|---|---|---|---|
| 1-1 | 3T(n/2) + n² | n^log₂3 ≈ n^1.585 < n² | 3 | Θ(n²) |
| 1-2 | 7T(n/2) + n² | n^log₂7 ≈ n^2.807 > n² | 1 | Θ(n^log₂7) |
| 1-3 | 4T(n/2) + n² | n^log₂4 = n² = n² | 2 (k=0) | Θ(n² log n) |
| 1-4 | 3T(n/4) + n lg n | n^log₄3 ≈ n^0.792 < n lg n | 3 | Θ(n lg n) |
| 1-5 | 4T(n/2) + lg n | n^log₂4 = n² > lg n | 1 | Θ(n²) |
| 1-6 | T(n-1) + n | not of the aT(n/b) form | N/A | Θ(n²) (by unrolling) |
| 1-7 | 4T(n/2) + n² lg n | n² = n², extra lg n factor | 2 (k=1) | Θ(n² lg²n) |
| 1-8 | 5T(n/2) + n² lg n | n^log₂5 ≈ n^2.32 > n² (lg n doesn't close a polynomial gap) | 1 | Θ(n^log₂5) |
| 1-9 | 3T(n/3) + n/lg n | n^log₃3 = n, but n/lg n isn't polynomially smaller | N/A | doesn't apply (gap case) |
| 1-10 | 2T(n/4) + c | n^log₄2 = n^0.5 > c = n^0 | 1 | Θ(n^0.5) |
| 1-11 | T(n/4) + lg n | n^log₄1 = n^0 = 1, extra lg n factor | 2 (k=1) | Θ(lg²n) |
| 1-12 | T(n/2) + T(n/4) + n² | uneven split, not aT(n/b) | N/A | Θ(n²) (recursion tree: top level alone is n², and the two branches' total work shrinks geometrically below it) |
| 1-13 | 2T(n/4) + lg n | n^log₄2 = n^0.5 > lg n | 1 | Θ(n^0.5) |
| 1-14 | 3T(n/3) + n lg n | n^log₃3 = n, extra lg n factor | 2 (k=1) | Θ(n lg²n) |
| 1-15 | 8T((n-√n)/4) + n² | subproblem size isn't cleanly n/b | N/A | doesn't strictly apply; sandwiching between 8T(n/4)+n² (gives Θ(n²), case 3 since n^log₄8=n^1.5<n²) and the fact that -√n only shrinks the subproblem further gives Θ(n²) either way |
| 1-16 | 2T(n/4) + √n | n^log₄2 = n^0.5 = √n | 2 (k=0) | Θ(n^0.5 lg n) |
| 1-17 | 2T(n/4) + n^0.51 | n^0.5 < n^0.51 (regularity: 2(n/4)^0.51 ≈ 0.986 n^0.51 < n^0.51, holds) | 3 | Θ(n^0.51) |
| 1-18 | 16T(n/4) + n! | n^log₄16 = n² ≪ n! | 3 | Θ(n!) |
| 1-19 | 3T(n/2) + n | n^log₂3 ≈ n^1.585 > n | 1 | Θ(n^log₂3) |
| 1-20 | 4T(n/2) + cn | n^log₂4 = n² > cn | 1 | Θ(n²) |
| 1-21 | 3T(n/3) + n/2 | n^log₃3 = n = n/2 (same order) | 2 (k=0) | Θ(n lg n) |
| 1-22 | 4T(n/2) + n/lg n | n^log₂4 = n² ≫ n/lg n | 1 | Θ(n²) |
| 1-23 | 7T(n/3) + n² | n^log₃7 ≈ n^1.771 < n² | 3 | Θ(n²) |
| 1-24 | 8T(n/3) + 2ⁿ | n^log₃8 ≈ n^1.893 ≪ 2ⁿ | 3 | Θ(2ⁿ) |
| 1-25 | 16T(n/4) + n | n^log₄16 = n² > n | 1 | Θ(n²) |

A few worth a sentence of extra explanation:

* **1-6 and 1-15** are not actually in the master theorem's form: 1-6 shrinks
  by subtracting 1 each time rather than dividing, and 1-15's subproblem size
  is `(n - √n)/4`, not a clean `n/4`. Both are still solvable (1-6 by writing
  out T(n) = n + (n-1) + (n-2) + ... = Θ(n²), 1-15 by noting the √n term is too
  small to change the outcome you'd get from the clean `8T(n/4) + n²` version),
  but neither is a direct master-theorem application.
* **1-9** is the classic "gap" case: n/lg n sits strictly between "polynomially
  smaller than n" (which case 1 needs) and "Θ(n) times a power of lg n" (which
  case 2 needs), because lg n grows slower than any positive power of n. The
  master theorem genuinely has no case for this; it needs a different method
  (one exists, giving Θ(n lg lg n), but deriving it isn't a master theorem
  exercise).
* **1-12** has two different recursive calls of different sizes in one
  recurrence (T(n/2) and T(n/4) together), which the master theorem's single
  `aT(n/b)` form can't represent at all. A recursion tree still works: the top
  level does n² work, and each subsequent level's total work is at most
  (1/2 + 1/4) = 3/4 of the level above it, a shrinking geometric series, so the
  total is dominated by the n² at the top: Θ(n²).
* **1-24**: the worksheet's PDF renders this problem's `2ⁿ` term as `2n` (the
  superscript is lost in the text extraction); the official answer is stated
  as Θ(2ⁿ), which only makes sense, and only gets marked case 3, if the term
  is exponential, so that's the reading used here.

---

*AI assistance: this writeup was produced with the help of Claude (Anthropic), under my direction and review.*
