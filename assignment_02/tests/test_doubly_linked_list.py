"""Tests for DoublyLinkedList.

The randomized tests cross-check against ``collections.deque``, which supports
the same six operations (appendleft/append/popleft/pop and their peeks) and is
a trustworthy oracle for what a correct doubly linked list should do.
"""

from __future__ import annotations

import random
from collections import deque

import pytest

from linked_structures import DoublyLinkedList


def test_new_list_is_empty() -> None:
    dll: DoublyLinkedList[int] = DoublyLinkedList()
    assert dll.is_empty() is True
    assert len(dll) == 0


@pytest.mark.parametrize(
    "method_name", ["pop_front", "pop_back", "peek_front", "peek_back"]
)
def test_read_on_empty_list_returns_none(method_name: str) -> None:
    dll: DoublyLinkedList[int] = DoublyLinkedList()
    assert getattr(dll, method_name)() is None


def test_push_front_single_element() -> None:
    dll: DoublyLinkedList[str] = DoublyLinkedList()
    dll.push_front("a")
    assert dll.is_empty() is False
    assert len(dll) == 1
    assert dll.peek_front() == "a"
    assert dll.peek_back() == "a"


def test_push_back_single_element() -> None:
    dll: DoublyLinkedList[str] = DoublyLinkedList()
    dll.push_back("a")
    assert dll.peek_front() == "a"
    assert dll.peek_back() == "a"


def test_push_front_multiple_orders_most_recent_first() -> None:
    dll: DoublyLinkedList[int] = DoublyLinkedList()
    for value in [1, 2, 3]:
        dll.push_front(value)
    assert list(dll) == [3, 2, 1]


def test_push_back_multiple_orders_most_recent_last() -> None:
    dll: DoublyLinkedList[int] = DoublyLinkedList()
    for value in [1, 2, 3]:
        dll.push_back(value)
    assert list(dll) == [1, 2, 3]


def test_mixed_push_front_and_back() -> None:
    dll: DoublyLinkedList[int] = DoublyLinkedList()
    dll.push_back(2)      # [2]
    dll.push_front(1)     # [1, 2]
    dll.push_back(3)      # [1, 2, 3]
    dll.push_front(0)     # [0, 1, 2, 3]
    assert list(dll) == [0, 1, 2, 3]
    assert len(dll) == 4


def test_pop_front_removes_in_order() -> None:
    dll: DoublyLinkedList[int] = DoublyLinkedList()
    for value in [1, 2, 3]:
        dll.push_back(value)
    assert dll.pop_front() == 1
    assert dll.pop_front() == 2
    assert dll.pop_front() == 3
    assert dll.pop_front() is None
    assert dll.is_empty() is True


def test_pop_back_removes_in_order() -> None:
    dll: DoublyLinkedList[int] = DoublyLinkedList()
    for value in [1, 2, 3]:
        dll.push_back(value)
    assert dll.pop_back() == 3
    assert dll.pop_back() == 2
    assert dll.pop_back() == 1
    assert dll.pop_back() is None
    assert dll.is_empty() is True


def test_single_element_pop_front_empties_the_list() -> None:
    dll: DoublyLinkedList[int] = DoublyLinkedList()
    dll.push_back(1)
    assert dll.pop_front() == 1
    assert dll.is_empty() is True
    assert dll.peek_front() is None
    assert dll.peek_back() is None
    # and it's usable again afterwards
    dll.push_back(2)
    assert dll.peek_front() == 2
    assert dll.peek_back() == 2


def test_single_element_pop_back_empties_the_list() -> None:
    dll: DoublyLinkedList[int] = DoublyLinkedList()
    dll.push_back(1)
    assert dll.pop_back() == 1
    assert dll.is_empty() is True
    assert dll.peek_front() is None
    assert dll.peek_back() is None


def test_peek_does_not_remove() -> None:
    dll: DoublyLinkedList[int] = DoublyLinkedList()
    dll.push_back(1)
    dll.push_back(2)
    assert dll.peek_front() == 1
    assert dll.peek_front() == 1
    assert len(dll) == 2


def test_len_tracks_pushes_and_pops() -> None:
    dll: DoublyLinkedList[int] = DoublyLinkedList()
    assert len(dll) == 0
    dll.push_back(1)
    dll.push_front(2)
    assert len(dll) == 2
    dll.pop_back()
    assert len(dll) == 1
    dll.pop_front()
    assert len(dll) == 0


def test_works_with_a_non_int_type() -> None:
    dll: DoublyLinkedList[str] = DoublyLinkedList()
    dll.push_back("first")
    dll.push_back("second")
    assert dll.pop_front() == "first"
    assert dll.pop_front() == "second"


# --------------------------------------------------------------------------- #
# Randomized cross-check against collections.deque
# --------------------------------------------------------------------------- #

_OPS = ["push_front", "push_back", "pop_front", "pop_back", "peek_front", "peek_back"]


@pytest.mark.parametrize("seed", range(50))
def test_matches_deque_for_random_operation_sequences(seed: int) -> None:
    rng = random.Random(seed)
    dll: DoublyLinkedList[int] = DoublyLinkedList()
    oracle: deque[int] = deque()

    for i in range(rng.randint(0, 100)):
        op = rng.choice(_OPS)
        if op == "push_front":
            dll.push_front(i)
            oracle.appendleft(i)
        elif op == "push_back":
            dll.push_back(i)
            oracle.append(i)
        elif op == "pop_front":
            expected = oracle.popleft() if oracle else None
            assert dll.pop_front() == expected
        elif op == "pop_back":
            expected = oracle.pop() if oracle else None
            assert dll.pop_back() == expected
        elif op == "peek_front":
            expected = oracle[0] if oracle else None
            assert dll.peek_front() == expected
        elif op == "peek_back":
            expected = oracle[-1] if oracle else None
            assert dll.peek_back() == expected

        assert dll.is_empty() == (len(oracle) == 0)
        assert len(dll) == len(oracle)

    assert list(dll) == list(oracle)
