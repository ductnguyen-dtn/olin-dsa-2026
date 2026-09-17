"""A LIFO stack, implemented as a thin wrapper around DoublyLinkedList."""

from __future__ import annotations

from typing import Generic, TypeVar

from linked_structures.doubly_linked_list import DoublyLinkedList

T = TypeVar("T")


class Stack(Generic[T]):
    """LIFO stack. Push and pop both happen at the front of the list, so
    every operation is O(1) and none of them touch the back."""

    def __init__(self) -> None:
        self._items: DoublyLinkedList[T] = DoublyLinkedList()

    def push(self, data: T) -> None:
        """Add ``data`` to the top of the stack."""
        self._items.push_front(data)

    def pop(self) -> T | None:
        """Remove and return the top of the stack, or None if empty."""
        return self._items.pop_front()

    def peek(self) -> T | None:
        """Return the top of the stack without removing it, or None if empty."""
        return self._items.peek_front()

    def is_empty(self) -> bool:
        """True if the stack holds no elements."""
        return self._items.is_empty()

    def __len__(self) -> int:
        return len(self._items)
