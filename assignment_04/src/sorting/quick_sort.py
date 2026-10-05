"""Quick sort.

Divide and conquer, like merge sort, but it splits differently: pick a pivot,
partition the list into "less than pivot" and "not less than pivot", then sort
each side recursively. There is no merge step, because by the time both sides
are sorted, the whole list already is (everything on the left is ≤ the pivot
and everything on the right is ≥ it).

Complexity (n = number of elements):

* Worst case: Θ(n²). This happens when every partition is maximally
  unbalanced, i.e. the pivot ends up at one end of its slice every single
  time, which turns the recursion into n nested calls each doing Θ(n) work
  (T(n) = T(n-1) + Θ(n)). A fixed pivot choice (always the first or last
  element) hits exactly this on input that is already sorted or reverse
  sorted, a very ordinary case to run into.
* Average case: Θ(n log n). As long as the pivot lands somewhere in the
  "middle fraction" of its slice on average (not even close to the median,
  just consistently not at the very edge), the recursion depth stays Θ(log n)
  and the partitioning work per level stays Θ(n). A *random* pivot, used
  here, makes every input have this average-case behavior: there is no input
  that reliably causes the worst case, because the bad case now depends on
  the random choices, not on the data.
* Space: Θ(log n) expected (the recursion stack; this implementation's
  partition step uses Θ(n) auxiliary space for its two side-lists rather than
  partitioning the array in place, which trades the usual in-place Θ(1) extra
  space for simpler, more obviously-correct partitioning code).
* Worth knowing: quick sort is *not stable* in general (a partition step can
  reorder equal elements relative to each other).
"""

from __future__ import annotations

import random

from sorting._comparable import T


def quick_sort(items: list[T]) -> list[T]:
    """Return a new list holding ``items`` in ascending order. ``items`` itself
    is not modified.

    Picks a uniformly random pivot at each level, so the Θ(n²) worst case
    depends on an unlucky run of random choices rather than on any particular
    input ordering (already-sorted input included).
    """
    if len(items) <= 1:
        return list(items)

    pivot = items[random.randrange(len(items))]
    less: list[T] = []
    equal: list[T] = []
    greater: list[T] = []
    for item in items:
        if item < pivot:
            less.append(item)
        elif pivot < item:
            greater.append(item)
        else:
            equal.append(item)  # neither item < pivot nor pivot < item: tied

    # `equal` needs no further sorting: every copy of the pivot value belongs
    # exactly here, between the smaller and bigger groups.
    return quick_sort(less) + equal + quick_sort(greater)
