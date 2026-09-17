"""Doubly linked list, and a Stack and Queue built on top of it.

``DoublyLinkedList`` is the one real data structure; ``Stack`` and ``Queue``
are thin adapters over it, each operation a one-liner that picks the right end
of the list. ``reverse_stack``, ``is_valid_parentheses`` and ``copy_stack`` are
the three stack/queue practice problems, built on ``Stack`` and ``Queue``.
"""

from linked_structures.doubly_linked_list import DoublyLinkedList
from linked_structures.stack import Stack
from linked_structures.fifo_queue import Queue
from linked_structures.reverse_stack import reverse_stack
from linked_structures.valid_parentheses import is_valid_parentheses
from linked_structures.copy_stack import copy_stack

__all__ = [
    "DoublyLinkedList",
    "Stack",
    "Queue",
    "reverse_stack",
    "is_valid_parentheses",
    "copy_stack",
]
