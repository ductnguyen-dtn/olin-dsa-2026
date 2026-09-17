"""Practice problem 4: valid parentheses.

Strategy: scan the string once, keeping a stack of the open brackets seen so
far. On a closing bracket, the top of the stack must be its matching open
bracket; if the stack is empty (a close with nothing open) or the top doesn't
match, the string is invalid. Any other character is ignored. At the end, the
string is valid only if every open bracket found a match: the stack must be
empty (nothing left unmatched).

O(n) time (one pass), O(n) worst-case space (a string of nothing but opens).
"""

from __future__ import annotations

from linked_structures.stack import Stack

# Every closing bracket maps to the open bracket it must match.
_MATCHING_OPEN = {")": "(", "]": "[", "}": "{"}


def is_valid_parentheses(expression: str) -> bool:
    """Return True if every bracket in ``expression`` is matched and nested
    correctly.

    Only ``()[]{}`` are treated as brackets; every other character is
    ignored, so this also works on strings that mix brackets with other text
    (code, for example).
    """
    open_brackets: Stack[str] = Stack()

    for char in expression:
        if char in _MATCHING_OPEN.values():
            # An opening bracket: remember it, it needs a match later.
            open_brackets.push(char)
        elif char in _MATCHING_OPEN:
            # A closing bracket: the most recently opened bracket must be its
            # match. `pop()` returns None on an empty stack, and None will
            # never equal a bracket character, so "closed with nothing open"
            # and "closed the wrong kind" both fall out of this one check.
            if open_brackets.pop() != _MATCHING_OPEN[char]:
                return False

    # Valid only if every opening bracket got matched: none left on the stack.
    return open_brackets.is_empty()
