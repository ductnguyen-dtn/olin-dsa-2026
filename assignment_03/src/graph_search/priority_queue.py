"""A min priority queue: the lower the priority value, the sooner an element
comes out. A thin wrapper over ``MinHeap``, matching the assignment's Kotlin
``MinPriorityQueue<T>`` interface translated to Python naming."""

from __future__ import annotations

from typing import Generic, Hashable, TypeVar

from graph_search.min_heap import MinHeap

T = TypeVar("T", bound=Hashable)


class MinPriorityQueue(Generic[T]):
    """Priority queue that removes the lowest-priority-value element first.

    Elements must be hashable and unique: the queue holds each element at most
    once, at one priority. That is what makes ``adjust_priority`` well defined
    ("the element", not "one of the copies") and O(log n).
    """

    def __init__(self) -> None:
        """Create an empty queue."""
        self._heap: MinHeap[T] = MinHeap()

    def is_empty(self) -> bool:
        """True if the queue holds no elements."""
        return self._heap.is_empty()

    def add_with_priority(self, elem: T, priority: float) -> None:
        """Add ``elem`` at level ``priority``.

        If ``elem`` is already in the queue, its priority is changed to
        ``priority`` instead of adding a second copy.
        """
        if elem in self._heap:
            self._heap.update(elem, priority)
        else:
            self._heap.push(elem, priority)

    def next(self) -> T | None:
        """Remove and return the element with the lowest priority value, or
        None if the queue is empty."""
        entry = self._heap.pop()
        return None if entry is None else entry[0]

    def adjust_priority(self, elem: T, new_priority: float) -> None:
        """Change the priority of ``elem`` to ``new_priority``. A lower value
        moves it earlier in the order, a higher value moves it later.

        Raises:
            KeyError: if ``elem`` is not in the queue.
        """
        self._heap.update(elem, new_priority)

    def __len__(self) -> int:
        """Number of elements in the queue."""
        return len(self._heap)

    def __contains__(self, elem: object) -> bool:
        """True if ``elem`` is in the queue."""
        return elem in self._heap
