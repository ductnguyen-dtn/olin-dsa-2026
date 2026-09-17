"""Practice problem 3: reverse a stack (the elements on top become the ones on
the bottom, and vice versa).

Strategy: draining a stack into a queue and back reverses it. Popping S gives
its values top-to-bottom, in order; a queue relays that same order unchanged
(FIFO does not reorder); pushing that order back onto S puts the last value on
top, which is exactly a reversal (a stack push always reverses whatever order
it is fed). So a single auxiliary queue is enough, no second stack needed.
Two passes, O(n) time, O(n) auxiliary space for the queue.

See docs/practice_problems.md for the strategies for exercises 4 and 5, and for
why exercise 5's "restore the stack, but also make a same-order copy" needs
this same trick applied *twice*.
"""

from __future__ import annotations

from typing import TypeVar

from linked_structures.fifo_queue import Queue
from linked_structures.stack import Stack

T = TypeVar("T")


def reverse_stack(stack: Stack[T]) -> None:
    """Reverse ``stack`` in place using one auxiliary Queue."""
    holding = Queue[T]()

    while not stack.is_empty():
        item = stack.pop()
        assert item is not None  # stack wasn't empty at the loop check
        holding.enqueue(item)

    while not holding.is_empty():
        item = holding.dequeue()
        assert item is not None  # holding wasn't empty at the loop check
        stack.push(item)
