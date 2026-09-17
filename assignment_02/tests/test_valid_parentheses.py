"""Tests for is_valid_parentheses (practice problem 4)."""

from __future__ import annotations

import pytest

from linked_structures import is_valid_parentheses


@pytest.mark.parametrize(
    "expression",
    [
        "",
        "()",
        "[]",
        "{}",
        "()[]{}",
        "([{}])",
        "{[()()]}",
        "(((())))",
        "a(b)c",              # brackets mixed with other characters
        "def f(x, [1, 2]):",  # looks like real code
    ],
)
def test_valid_examples(expression: str) -> None:
    assert is_valid_parentheses(expression) is True


@pytest.mark.parametrize(
    "expression",
    [
        "(",
        ")",
        "(()",
        "())",
        "(]",
        "([)]",       # interleaved, not nested
        "{[}]",       # interleaved, not nested
        "]",
        "((((",
        ")))(",
    ],
)
def test_invalid_examples(expression: str) -> None:
    assert is_valid_parentheses(expression) is False


def test_non_bracket_characters_are_ignored() -> None:
    assert is_valid_parentheses("no brackets at all here") is True


def test_close_with_nothing_open_is_invalid_even_mid_string() -> None:
    assert is_valid_parentheses("()) (") is False
