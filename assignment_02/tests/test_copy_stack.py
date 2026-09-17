"""Tests for copy_stack (practice problem 5)."""

from __future__ import annotations

import random

import pytest

from linked_structures import Stack, copy_stack


def _to_list(stack: Stack[int]) -> list[int]:
    """Drain a stack top-to-bottom into a list, leaving it empty."""
    values = []
    while not stack.is_empty():
        item = stack.pop()
        assert item is not None
        values.append(item)
    return values


def _from_list(values: list[int]) -> Stack[int]:
    """Build a stack by pushing values in order, so the last one ends up on top."""
    stack: Stack[int] = Stack()
    for v in values:
        stack.push(v)
    return stack


def test_copy_of_empty_stack_is_empty() -> None:
    original: Stack[int] = Stack()
    copy = copy_stack(original)
    assert copy.is_empty() is True
    assert original.is_empty() is True


def test_copy_matches_original_order() -> None:
    original = _from_list([1, 2, 3])
    copy = copy_stack(original)
    assert _to_list(copy) == [3, 2, 1]


def test_original_is_left_unchanged() -> None:
    values = [1, 2, 3, 4, 5]
    original = _from_list(values)
    copy_stack(original)
    assert _to_list(original) == _to_list(_from_list(values))


def test_copy_is_independent_of_the_original() -> None:
    original = _from_list([1, 2, 3])
    copy = copy_stack(original)

    copy.pop()
    copy.push(99)
    # Mutating the copy must not have touched the original.
    assert _to_list(original) == [3, 2, 1]


def test_single_element() -> None:
    original = _from_list([42])
    copy = copy_stack(original)
    assert _to_list(copy) == [42]
    assert _to_list(original) == [42]


@pytest.mark.parametrize("seed", range(30))
def test_matches_original_and_leaves_it_intact_for_random_stacks(seed: int) -> None:
    rng = random.Random(seed)
    values = [rng.randint(0, 100) for _ in range(rng.randint(0, 20))]
    expected_top_to_bottom = _to_list(_from_list(values))

    original = _from_list(values)
    copy = copy_stack(original)

    assert _to_list(copy) == expected_top_to_bottom
    assert _to_list(original) == expected_top_to_bottom
