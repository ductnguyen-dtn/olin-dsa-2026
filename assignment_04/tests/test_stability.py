"""Stability: do elements that compare equal keep their original relative
order?

Insertion sort and merge sort are stable; this file's quick sort and heap
sort are not guaranteed to be (see their docstrings for why). Tested by
sorting ``(key, original_index)`` pairs ordered by key only, then checking
that pairs sharing a key still appear in increasing original-index order.
"""

from __future__ import annotations

from sorting import insertion_sort, merge_sort


class _KeyOnly:
    """Wraps a (key, original_index) pair so ``<`` only looks at the key,
    exactly like sorting real records by one field while carrying the rest
    of the record along."""

    def __init__(self, key: int, index: int) -> None:
        self.key = key
        self.index = index

    def __lt__(self, other: object) -> bool:
        assert isinstance(other, _KeyOnly)
        return self.key < other.key

    def __repr__(self) -> str:
        return f"_KeyOnly({self.key}, {self.index})"


def _is_stable(sorted_items: list[_KeyOnly]) -> bool:
    """True if, within every run of equal keys, indices are increasing."""
    for a, b in zip(sorted_items, sorted_items[1:]):
        if a.key == b.key and a.index > b.index:
            return False
    return True


def _tagged(keys: list[int]) -> list[_KeyOnly]:
    return [_KeyOnly(key, i) for i, key in enumerate(keys)]


def test_insertion_sort_is_stable() -> None:
    items = _tagged([3, 1, 3, 2, 1, 3])
    result = insertion_sort(items)
    assert [k.key for k in result] == [1, 1, 2, 3, 3, 3]
    assert _is_stable(result)


def test_merge_sort_is_stable() -> None:
    items = _tagged([3, 1, 3, 2, 1, 3])
    result = merge_sort(items)
    assert [k.key for k in result] == [1, 1, 2, 3, 3, 3]
    assert _is_stable(result)
