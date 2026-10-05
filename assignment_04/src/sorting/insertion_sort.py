"""Insertion sort.

Builds up a sorted prefix of the list one element at a time: for each new
element, slide it left past every already-sorted element that is bigger than
it, so it lands in the correct spot among them.

Complexity (n = number of elements):

* Worst case: Θ(n²). The input is in reverse order, so every new element has
  to slide past all of the sorted prefix before it.
* Best case: Θ(n). The input is already sorted, so the inner "slide left"
  step never has anything bigger to slide past: one comparison, no moves,
  per element.
* Average case: Θ(n²). For a random ordering, a new element is expected to
  slide past about half of the sorted prefix.
* Space: Θ(1) extra (sorts in place on its working copy; no recursion).
* Not used here, but worth knowing: insertion sort is *stable* (equal
  elements keep their original relative order, since an element only moves
  past strictly-greater ones) and fast on nearly-sorted input, which is why
  real-world sorts (Python's Timsort included) fall back to it for small or
  already-mostly-sorted runs instead of using it as the whole algorithm.
"""

from __future__ import annotations

from sorting._comparable import T


def insertion_sort(items: list[T]) -> list[T]:
    """Return a new list holding ``items`` in ascending order. ``items`` itself
    is not modified."""
    result = list(items)
    for i in range(1, len(result)):
        current = result[i]
        j = i - 1
        # Shift every sorted element bigger than `current` one slot to the
        # right, opening up the gap `current` belongs in.
        while j >= 0 and current < result[j]:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = current
    return result
