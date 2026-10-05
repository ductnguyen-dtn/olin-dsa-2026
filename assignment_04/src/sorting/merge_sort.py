"""Merge sort.

Classic divide and conquer: split the list in half, sort each half
recursively, then merge the two sorted halves into one sorted list by
repeatedly taking the smaller of the two fronts.

Complexity (n = number of elements):

* Worst, best, and average case: Θ(n log n), always. Unlike insertion or
  quick sort, merge sort's split is purely by position (always exactly in
  half), so its runtime does not depend on the input's order at all. The
  recurrence is T(n) = 2T(n/2) + Θ(n) (two half-size subproblems, plus a
  linear-time merge); by the master theorem this is case 2, giving Θ(n log n).
* Space: Θ(n) extra. The merge step needs a second buffer to hold the merged
  result while reading from both halves, and that buffer is proportional to
  the slice being merged. This is the price merge sort pays for guaranteed
  Θ(n log n): unlike heap sort or (typical) quick sort, it is not in place.
* Worth knowing: merge sort is *stable* (the merge step takes from the left
  half on ties, so equal elements keep their original relative order).
"""

from __future__ import annotations

from sorting._comparable import T


def merge_sort(items: list[T]) -> list[T]:
    """Return a new list holding ``items`` in ascending order. ``items`` itself
    is not modified."""
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    left = merge_sort(items[:mid])
    right = merge_sort(items[mid:])
    return _merge(left, right)


def _merge(left: list[T], right: list[T]) -> list[T]:
    """Merge two already-sorted lists into one sorted list."""
    merged: list[T] = []
    i = j = 0
    while i < len(left) and j < len(right):
        # Taking from the left on a tie (not left[i] < right[j]) rather than
        # only on a strict left[i] < right[j] keeps the merge stable: when the
        # fronts are equal, the one from the left half goes first, matching
        # the order it had before the split. Written with `__lt__` only, to
        # match the same _Comparable bound every sort in this package uses.
        if not right[j] < left[i]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    # One side is now empty; the rest of the other side is already sorted and
    # already bigger than everything merged so far, so it can be appended as is.
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged
