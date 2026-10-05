"""Heap sort.

Two phases, both done in place on one array:

1. **Heapify**: rearrange the array into a max heap (every parent is ≥ both
   its children), using the same implicit array layout as ``MinHeap`` in
   Assignment 3's ``graph_search`` package (parent at ``i``, children at
   ``2i + 1`` and ``2i + 2``), but inverted to a *max* heap, so the largest
   element ends up at index 0.
2. **Sort down**: the max heap's largest element is always at index 0, which
   is also where the sorted result's last slot is. Repeatedly swap index 0
   with the current last unsorted slot, shrink the heap by one, and sift the
   new root down to restore the heap property. Each swap places one more
   element in its final sorted position, from the back of the array forward.

Complexity (n = number of elements):

* Worst, best, and average case: Θ(n log n), always, regardless of the input's
  order. Building the heap is Θ(n) (not Θ(n log n): most nodes are near the
  bottom of the tree and need very little sifting, and the sum works out
  linear). The sort-down phase does n swap-and-sift-down steps, each
  Θ(log n) (the heap's height), for Θ(n log n) total. There is no
  input-dependent worst case the way quick sort has, because which element is
  biggest does not change how much work sifting it down takes, only the heap
  shape (always a complete binary tree) does.
* Space: Θ(1) extra. Unlike merge sort, the heap is built in the same array
  being sorted; unlike this file's quick sort, there is no per-call auxiliary
  list. This is heap sort's main selling point: Θ(n log n) guaranteed, in
  place.
* Worth knowing: heap sort is *not stable* (sifting can reorder equal
  elements), and in practice tends to run slower than a well-tuned quick sort
  on random data despite having the better worst case, because its memory
  access pattern (jumping between parent and child indices) is less
  cache-friendly than quick sort's or merge sort's mostly-sequential one.
"""

from __future__ import annotations

from sorting._comparable import T


def heap_sort(items: list[T]) -> list[T]:
    """Return a new list holding ``items`` in ascending order. ``items`` itself
    is not modified."""
    result = list(items)
    n = len(result)

    # Phase 1: heapify. Every index past n // 2 is a leaf (no children), so
    # leaves are already trivially valid one-node heaps; only the non-leaves
    # need sifting, and sifting them from the bottom up guarantees that by the
    # time a node is sifted, both its children already root valid subheaps.
    for root in range(n // 2 - 1, -1, -1):
        _sift_down(result, root, n)

    # Phase 2: sort down. The largest remaining element is always at index 0;
    # move it to the end of the still-unsorted region, then restore the heap
    # property over the one element shorter heap.
    for end in range(n - 1, 0, -1):
        result[0], result[end] = result[end], result[0]
        _sift_down(result, 0, end)

    return result


def _sift_down(items: list[T], root: int, heap_size: int) -> None:
    """Restore the max-heap property at ``root``, assuming both its subtrees
    (within the first ``heap_size`` elements of ``items``) already satisfy it."""
    while True:
        left = 2 * root + 1
        right = left + 1
        largest = root
        if left < heap_size and items[largest] < items[left]:
            largest = left
        if right < heap_size and items[largest] < items[right]:
            largest = right
        if largest == root:
            return  # both children are already no bigger than this node
        items[root], items[largest] = items[largest], items[root]
        root = largest
