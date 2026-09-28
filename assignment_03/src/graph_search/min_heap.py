"""A binary min heap that supports changing an item's priority in place.

The heap is stored in a Python list using the standard implicit layout: the
node at index ``i`` has its children at ``2i + 1`` and ``2i + 2`` and its parent
at ``(i - 1) // 2``. The heap property is that every node's priority is less
than or equal to its children's, so the smallest priority is always at index 0.

To change an item's priority quickly, a second dict remembers where each item
currently sits in the list. Without it, finding an item would be a linear scan;
with it, ``update`` costs O(log n).

Cost summary (n = number of items):

* ``push``, ``pop``, ``update``: O(log n)
* ``peek``, ``is_empty``, ``len``, ``in``, ``priority_of``: O(1)
"""

from __future__ import annotations

import math
from typing import Generic, Hashable, TypeVar

T = TypeVar("T", bound=Hashable)


class MinHeap(Generic[T]):
    """Min heap of unique hashable items, each with a float priority."""

    def __init__(self) -> None:
        """Create an empty heap."""
        # The heap itself: (priority, item) pairs in implicit binary-tree order.
        self._entries: list[tuple[float, T]] = []
        # Where each item currently sits in ``_entries``. Must be kept in sync
        # on every move; ``_swap`` is the only place entries move.
        self._index: dict[T, int] = {}

    def __len__(self) -> int:
        """Number of items in the heap."""
        return len(self._entries)

    def __contains__(self, item: object) -> bool:
        """True if ``item`` is in the heap."""
        return item in self._index

    def is_empty(self) -> bool:
        """True if the heap holds no items."""
        return not self._entries

    def priority_of(self, item: T) -> float:
        """Return the current priority of ``item``.

        Raises:
            KeyError: if ``item`` is not in the heap.
        """
        return self._entries[self._index[item]][0]

    def peek(self) -> tuple[T, float] | None:
        """Return the ``(item, priority)`` with the smallest priority without
        removing it, or None if the heap is empty."""
        if not self._entries:
            return None
        priority, item = self._entries[0]
        return item, priority

    def push(self, item: T, priority: float) -> None:
        """Add ``item`` with the given ``priority``.

        Raises:
            ValueError: if ``item`` is already in the heap (use ``update`` to
                change its priority) or ``priority`` is NaN.
        """
        self._check_priority(priority)
        if item in self._index:
            raise ValueError(f"{item!r} is already in the heap")
        # Put the new item in the first free slot at the bottom, then let it
        # float up until its parent is no larger than it.
        self._entries.append((priority, item))
        self._index[item] = len(self._entries) - 1
        self._sift_up(len(self._entries) - 1)

    def pop(self) -> tuple[T, float] | None:
        """Remove and return the ``(item, priority)`` with the smallest
        priority, or None if the heap is empty."""
        if not self._entries:
            return None
        priority, item = self._entries[0]
        last = len(self._entries) - 1
        # Move the last entry into the root's slot, drop the old root off the
        # end, then let the moved entry sink to where it belongs. Doing it this
        # way keeps the list contiguous, which the implicit layout requires.
        self._swap(0, last)
        self._entries.pop()
        del self._index[item]
        if self._entries:
            self._sift_down(0)
        return item, priority

    def update(self, item: T, new_priority: float) -> None:
        """Change the priority of ``item`` to ``new_priority``.

        Raises:
            KeyError: if ``item`` is not in the heap.
            ValueError: if ``new_priority`` is NaN.
        """
        self._check_priority(new_priority)
        position = self._index[item]
        self._entries[position] = (new_priority, item)
        # The new priority may be smaller (must move up) or larger (must move
        # down) than before. At most one of these two calls will actually move
        # the entry; the other sees the heap property already holds and stops.
        self._sift_up(position)
        self._sift_down(self._index[item])

    @staticmethod
    def _check_priority(priority: float) -> None:
        """Reject NaN, which compares false to everything and would silently
        break the heap ordering."""
        if math.isnan(priority):
            raise ValueError("priority must not be NaN")

    def _swap(self, i: int, j: int) -> None:
        """Swap the entries at positions ``i`` and ``j``, updating ``_index``."""
        self._entries[i], self._entries[j] = self._entries[j], self._entries[i]
        self._index[self._entries[i][1]] = i
        self._index[self._entries[j][1]] = j

    def _sift_up(self, position: int) -> None:
        """Move the entry at ``position`` up while it is smaller than its parent."""
        while position > 0:
            parent = (position - 1) // 2
            if self._entries[position][0] >= self._entries[parent][0]:
                break
            self._swap(position, parent)
            position = parent

    def _sift_down(self, position: int) -> None:
        """Move the entry at ``position`` down while a child is smaller than it."""
        size = len(self._entries)
        while True:
            left = 2 * position + 1
            right = left + 1
            # Find the smallest of this entry and its (up to two) children.
            smallest = position
            if left < size and self._entries[left][0] < self._entries[smallest][0]:
                smallest = left
            if right < size and self._entries[right][0] < self._entries[smallest][0]:
                smallest = right
            if smallest == position:
                break
            self._swap(position, smallest)
            position = smallest
