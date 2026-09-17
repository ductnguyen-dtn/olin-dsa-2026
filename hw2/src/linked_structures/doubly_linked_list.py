"""A generic doubly linked list.

Matches the assignment's Kotlin interface, translated to Python naming
(``pushFront`` -> ``push_front``, etc). Every operation named in the
interface touches only the head or tail node, so every one of them is O(1).

Like the Kotlin interface it implements (methods return ``T?``), a "pop"
or "peek" on an empty list returns ``None`` rather than raising. That means
``None`` cannot be distinguished from "stored the value None" if this list is
ever used to hold optional values themselves; the assignment's own interface
has that same limitation, so it is kept here rather than fixed with a design
this port doesn't otherwise need.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterator, TypeVar

T = TypeVar("T")


@dataclass
class _Node(Generic[T]):
    value: T
    prev: _Node[T] | None = None
    next: _Node[T] | None = None


class DoublyLinkedList(Generic[T]):
    """Doubly linked list with O(1) push/pop/peek at both ends."""

    def __init__(self) -> None:
        self._head: _Node[T] | None = None
        self._tail: _Node[T] | None = None
        self._size = 0

    def push_front(self, data: T) -> None:
        """Add ``data`` to the front of the list."""
        node = _Node(data, prev=None, next=self._head)
        if self._head is not None:
            self._head.prev = node
        self._head = node
        if self._tail is None:
            self._tail = node
        self._size += 1

    def push_back(self, data: T) -> None:
        """Add ``data`` to the back of the list."""
        node = _Node(data, prev=self._tail, next=None)
        if self._tail is not None:
            self._tail.next = node
        self._tail = node
        if self._head is None:
            self._head = node
        self._size += 1

    def pop_front(self) -> T | None:
        """Remove and return the value at the front, or None if empty."""
        if self._head is None:
            return None
        node = self._head
        self._head = node.next
        if self._head is not None:
            self._head.prev = None
        else:
            self._tail = None
        self._size -= 1
        return node.value

    def pop_back(self) -> T | None:
        """Remove and return the value at the back, or None if empty."""
        if self._tail is None:
            return None
        node = self._tail
        self._tail = node.prev
        if self._tail is not None:
            self._tail.next = None
        else:
            self._head = None
        self._size -= 1
        return node.value

    def peek_front(self) -> T | None:
        """Return the value at the front without removing it, or None if empty."""
        return self._head.value if self._head is not None else None

    def peek_back(self) -> T | None:
        """Return the value at the back without removing it, or None if empty."""
        return self._tail.value if self._tail is not None else None

    def is_empty(self) -> bool:
        """True if the list holds no elements."""
        return self._head is None

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        """Front-to-back iteration, for tests and debugging."""
        node = self._head
        while node is not None:
            yield node.value
            node = node.next

    def __repr__(self) -> str:
        return f"DoublyLinkedList([{', '.join(repr(v) for v in self)}])"
