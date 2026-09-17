"""Tests for Stack. Randomized tests cross-check against a plain Python list
used as a stack (append/pop from the end), a trustworthy LIFO oracle."""

from __future__ import annotations

import random

import pytest

from linked_structures import Stack


def test_new_stack_is_empty() -> None:
    s: Stack[int] = Stack()
    assert s.is_empty() is True
    assert len(s) == 0


def test_pop_on_empty_returns_none() -> None:
    s: Stack[int] = Stack()
    assert s.pop() is None


def test_peek_on_empty_returns_none() -> None:
    s: Stack[int] = Stack()
    assert s.peek() is None


def test_push_then_peek_does_not_remove() -> None:
    s: Stack[int] = Stack()
    s.push(1)
    assert s.peek() == 1
    assert s.peek() == 1
    assert len(s) == 1


def test_lifo_order() -> None:
    s: Stack[int] = Stack()
    s.push(1)
    s.push(2)
    s.push(3)
    assert s.pop() == 3
    assert s.pop() == 2
    assert s.pop() == 1
    assert s.is_empty() is True


def test_pop_returns_none_once_drained() -> None:
    s: Stack[int] = Stack()
    s.push(1)
    s.pop()
    assert s.pop() is None
    assert s.peek() is None


def test_usable_again_after_being_emptied() -> None:
    s: Stack[int] = Stack()
    s.push(1)
    s.pop()
    s.push(2)
    assert s.peek() == 2
    assert s.is_empty() is False


@pytest.mark.parametrize("seed", range(50))
def test_matches_a_python_list_used_as_a_stack(seed: int) -> None:
    rng = random.Random(seed)
    s: Stack[int] = Stack()
    oracle: list[int] = []

    for i in range(rng.randint(0, 100)):
        op = rng.choice(["push", "pop", "peek"])
        if op == "push":
            s.push(i)
            oracle.append(i)
        elif op == "pop":
            expected = oracle.pop() if oracle else None
            assert s.pop() == expected
        else:
            expected = oracle[-1] if oracle else None
            assert s.peek() == expected

        assert s.is_empty() == (len(oracle) == 0)
        assert len(s) == len(oracle)
