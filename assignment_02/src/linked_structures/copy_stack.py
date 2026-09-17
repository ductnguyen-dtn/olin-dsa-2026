"""Practice problem 5: copy a stack, using one queue as auxiliary storage.

Source: University of Washington CSE122. Goal: given a stack, return a new
stack with the same values in the same order, using one queue as the only
extra storage, and leave the original stack the way it started.

Building block: reverse_stack. Worth being explicit about why this needs two
passes through that trick and not one: a single drain-into-a-queue-and-back
does not restore a stack's order, it reverses it (see reverse_stack's
docstring), so restoring the original order takes that reversal applied
twice, and the copy can be built for free on the second pass.

O(n) time (four linear passes total), O(n) auxiliary space for the queue.
"""

from __future__ import annotations

from typing import TypeVar

from linked_structures.fifo_queue import Queue
from linked_structures.reverse_stack import reverse_stack
from linked_structures.stack import Stack

T = TypeVar("T")


def copy_stack(stack: Stack[T]) -> Stack[T]:
    """Return a new stack holding the same values as ``stack``, in the same
    order, using one auxiliary Queue. ``stack`` itself is left unchanged.
    """
    # Phase A: reverse `stack` (see reverse_stack). It's now backwards.
    reverse_stack(stack)

    copy: Stack[T] = Stack()
    holding: Queue[T] = Queue()

    # Phase B: drain the now-reversed stack into the queue. A queue's FIFO
    # order doesn't reorder anything, so `holding` comes out dequeue-order
    # equal to `stack`'s (reversed) pop order.
    while not stack.is_empty():
        item = stack.pop()
        assert item is not None  # stack wasn't empty at the loop check
        holding.enqueue(item)

    # Pushing that dequeue order onto a stack reverses it again, which
    # cancels Phase A's reversal. Doing it to both `stack` and `copy` at once
    # restores the original and builds a matching copy in the same step.
    while not holding.is_empty():
        item = holding.dequeue()
        assert item is not None  # holding wasn't empty at the loop check
        stack.push(item)
        copy.push(item)

    return copy
