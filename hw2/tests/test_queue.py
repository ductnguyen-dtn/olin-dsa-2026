"""Tests for Queue. Randomized tests cross-check against collections.deque
used as a FIFO (append/popleft), a trustworthy oracle."""

from __future__ import annotations

import random
from collections import deque

import pytest

from linked_structures import Queue


def test_new_queue_is_empty() -> None:
    q: Queue[int] = Queue()
    assert q.is_empty() is True
    assert len(q) == 0


def test_dequeue_on_empty_returns_none() -> None:
    q: Queue[int] = Queue()
    assert q.dequeue() is None


def test_peek_on_empty_returns_none() -> None:
    q: Queue[int] = Queue()
    assert q.peek() is None


def test_enqueue_then_peek_does_not_remove() -> None:
    q: Queue[int] = Queue()
    q.enqueue(1)
    assert q.peek() == 1
    assert q.peek() == 1
    assert len(q) == 1


def test_fifo_order() -> None:
    q: Queue[int] = Queue()
    q.enqueue(1)
    q.enqueue(2)
    q.enqueue(3)
    assert q.dequeue() == 1
    assert q.dequeue() == 2
    assert q.dequeue() == 3
    assert q.is_empty() is True


def test_dequeue_returns_none_once_drained() -> None:
    q: Queue[int] = Queue()
    q.enqueue(1)
    q.dequeue()
    assert q.dequeue() is None
    assert q.peek() is None


def test_usable_again_after_being_emptied() -> None:
    q: Queue[int] = Queue()
    q.enqueue(1)
    q.dequeue()
    q.enqueue(2)
    assert q.peek() == 2
    assert q.is_empty() is False


@pytest.mark.parametrize("seed", range(50))
def test_matches_deque_used_as_a_fifo(seed: int) -> None:
    rng = random.Random(seed)
    q: Queue[int] = Queue()
    oracle: deque[int] = deque()

    for i in range(rng.randint(0, 100)):
        op = rng.choice(["enqueue", "dequeue", "peek"])
        if op == "enqueue":
            q.enqueue(i)
            oracle.append(i)
        elif op == "dequeue":
            expected = oracle.popleft() if oracle else None
            assert q.dequeue() == expected
        else:
            expected = oracle[0] if oracle else None
            assert q.peek() == expected

        assert q.is_empty() == (len(oracle) == 0)
        assert len(q) == len(oracle)
