"""A FIFO queue, implemented as a thin wrapper around DoublyLinkedList.

Named ``fifo_queue`` rather than ``queue`` so it can't be confused with (or
shadow) the standard library's ``queue`` module.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from linked_structures.doubly_linked_list import DoublyLinkedList

T = TypeVar("T")


class Queue(Generic[T]):
    """FIFO queue. Enqueue at the back, dequeue from the front, so every
    operation is O(1)."""

    def __init__(self) -> None:
        self._items: DoublyLinkedList[T] = DoublyLinkedList()

    def enqueue(self, data: T) -> None:
        """Add ``data`` to the back of the queue."""
        self._items.push_back(data)

    def dequeue(self) -> T | None:
        """Remove and return the front of the queue, or None if empty."""
        return self._items.pop_front()

    def peek(self) -> T | None:
        """Return the front of the queue without removing it, or None if empty."""
        return self._items.peek_front()

    def is_empty(self) -> bool:
        """True if the queue holds no elements."""
        return self._items.is_empty()

    def __len__(self) -> int:
        return len(self._items)
