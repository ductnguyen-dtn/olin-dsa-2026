# Complexity analysis

Full reasoning for each algorithm is in its module's docstring
(`src/sorting/*.py`); this is the summary. n = number of elements.

| Algorithm | Best | Average | Worst | Extra space | Stable? |
|---|---|---|---|---|---|
| Insertion sort | Θ(n) | Θ(n²) | Θ(n²) | Θ(1) | Yes |
| Merge sort | Θ(n log n) | Θ(n log n) | Θ(n log n) | Θ(n) | Yes |
| Quick sort (random pivot) | Θ(n log n) | Θ(n log n) | Θ(n²) | Θ(log n) expected (recursion) + Θ(n) per level for this implementation's side-lists | No |
| Heap sort | Θ(n log n) | Θ(n log n) | Θ(n log n) | Θ(1) | No |

## Why each one lands where it does

**Insertion sort** does one pass per element, and each pass slides the new
element left past every already-sorted element bigger than it. On sorted
input nothing is ever bigger, so each pass is O(1): Θ(n) overall. On reverse
sorted input every pass slides all the way to the front: 1 + 2 + ... + (n-1)
≈ n²/2 total shifts, Θ(n²). A random ordering slides past about half the
sorted prefix on average, which is still Θ(n²), just with a smaller constant.

**Merge sort**'s split is always exactly in half regardless of the data, so
its recurrence is always T(n) = 2T(n/2) + Θ(n) (two half-size subproblems,
Θ(n) to merge them back together). By the master theorem this is case 2
(a = 2, b = 2, f(n) = Θ(n) = Θ(n^log₂2)), giving Θ(n log n) in every case.
The Θ(n) extra space is the merge step's buffer, needed because merging two
sorted halves in place without it is not straightforward.

**Quick sort**'s recurrence depends on how balanced the partition is, which
depends on the pivot. A pivot that always lands at one end gives
T(n) = T(n-1) + Θ(n), which unrolls to Θ(n²) (the same arithmetic series as
insertion sort's worst case). A pivot that lands anywhere in the "middle
fraction" of its slice, even consistently off-center, keeps the recursion
depth at Θ(log n) with Θ(n) partitioning work per level, giving Θ(n log n).
This implementation picks the pivot uniformly at random specifically so that
no particular *input* can reliably trigger the Θ(n²) case (already-sorted
data, which breaks a fixed first-or-last-element pivot choice, is just as
fast as random data here): the worst case still exists, but it now depends
on an unlucky sequence of random choices rather than on the data.

**Heap sort** builds a max heap in Θ(n) (most nodes are near the bottom of
the tree and need very little sifting; the per-node sift costs decrease
geometrically going up the tree, which sums to a linear total rather than
the Θ(n log n) a naive per-node bound would suggest), then does n
extract-max steps at Θ(log n) each (the heap's height), for Θ(n log n)
total. Nothing about this depends on the input's order, only on the fact
that it is always a complete binary tree of height ⌊log₂n⌋, so heap sort has
no input-dependent worst case.

## Why benchmarking still shows real differences between the Θ(n log n) ones

Θ notation hides constant factors, and those constants are not equal in
practice. Merge sort allocates a new list on every merge (Python-level list
`extend`/`append` calls add real overhead on top of the comparisons). Heap
sort's array-index arithmetic jumps around the array (parent/child indices),
which is less cache-friendly than merge sort's or quick sort's mostly
sequential access. Quick sort does the least bookkeeping per comparison in
this implementation. The benchmark in `docs/benchmarking.md` shows this:
same Θ(n log n) class, different actual runtimes.
