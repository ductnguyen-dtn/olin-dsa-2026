"""Doubly linked list, and a Stack and Queue built on top of it.

``DoublyLinkedList`` is the one real data structure; ``Stack`` and ``Queue``
are thin adapters over it, each operation a one-liner that picks the right end
of the list.
"""

from linked_structures.doubly_linked_list import DoublyLinkedList
from linked_structures.stack import Stack
from linked_structures.fifo_queue import Queue

__all__ = ["DoublyLinkedList", "Stack", "Queue"]
