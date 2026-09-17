"""Tests for reverse_stack (practice problem 3)."""

from __future__ import annotations

from linked_structures import Stack
from linked_structures.reverse_stack import reverse_stack


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


def test_reverse_empty_stack_stays_empty() -> None:
    s: Stack[int] = Stack()
    reverse_stack(s)
    assert s.is_empty() is True


def test_reverse_single_element() -> None:
    s: Stack[int] = Stack()
    s.push(1)
    reverse_stack(s)
    assert _to_list(s) == [1]


def test_reverse_puts_top_on_bottom_and_bottom_on_top() -> None:
    # push order 1, 2, 3 -> top-to-bottom before reversing: [3, 2, 1]
    assert _to_list(_from_list([1, 2, 3])) == [3, 2, 1]  # sanity check on the setup

    s = _from_list([1, 2, 3])
    reverse_stack(s)
    assert _to_list(s) == [1, 2, 3]


def test_reverse_preserves_length() -> None:
    s = _from_list([1, 2, 3, 4, 5])
    reverse_stack(s)
    assert len(s) == 5


def test_reverse_twice_restores_the_original_order() -> None:
    original = [5, 4, 3, 2, 1]
    s = _from_list(original)
    reverse_stack(s)
    reverse_stack(s)
    assert _to_list(s) == _to_list(_from_list(original))
