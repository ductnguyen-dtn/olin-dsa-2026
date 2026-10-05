"""Tests shared by all four sorting algorithms.

Every algorithm has to satisfy the same contract (a correct sort, input
untouched), so those properties are tested once, parametrized over all four
implementations, rather than copy-pasted four times. Algorithm-specific
properties (merge/insertion sort's stability, heap/quick sort's explicit lack
of it) have their own test files.
"""

from __future__ import annotations

import random
from typing import Callable, TypeVar, cast

import pytest

from sorting import heap_sort, insertion_sort, merge_sort, quick_sort

T = TypeVar("T")
SortFn = Callable[[list[T]], list[T]]

# Each sort function is generic (Callable[[list[T]], list[T]]); mypy does not
# auto-specialize a bare generic-function reference when it goes straight into
# a list literal typed for one concrete T, so the casts below just assert the
# specialization that calling each function at a given T would infer anyway.
_RAW = [insertion_sort, merge_sort, quick_sort, heap_sort]
ALGORITHMS: list[SortFn[int]] = [cast(SortFn[int], fn) for fn in _RAW]
ALGORITHMS_STR: list[SortFn[str]] = [cast(SortFn[str], fn) for fn in _RAW]
ALGORITHMS_FLOAT: list[SortFn[float]] = [cast(SortFn[float], fn) for fn in _RAW]


@pytest.mark.parametrize("sort", ALGORITHMS)
def test_empty_list(sort: SortFn[int]) -> None:
    assert sort([]) == []


@pytest.mark.parametrize("sort", ALGORITHMS)
def test_single_element(sort: SortFn[int]) -> None:
    assert sort([5]) == [5]


@pytest.mark.parametrize("sort", ALGORITHMS)
def test_two_elements_already_in_order(sort: SortFn[int]) -> None:
    assert sort([1, 2]) == [1, 2]


@pytest.mark.parametrize("sort", ALGORITHMS)
def test_two_elements_out_of_order(sort: SortFn[int]) -> None:
    assert sort([2, 1]) == [1, 2]


@pytest.mark.parametrize("sort", ALGORITHMS)
def test_already_sorted_input(sort: SortFn[int]) -> None:
    assert sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]


@pytest.mark.parametrize("sort", ALGORITHMS)
def test_reverse_sorted_input(sort: SortFn[int]) -> None:
    assert sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]


@pytest.mark.parametrize("sort", ALGORITHMS)
def test_all_elements_equal(sort: SortFn[int]) -> None:
    assert sort([7, 7, 7, 7]) == [7, 7, 7, 7]


@pytest.mark.parametrize("sort", ALGORITHMS)
def test_duplicates_mixed_with_distinct_values(sort: SortFn[int]) -> None:
    assert sort([3, 1, 2, 3, 1]) == [1, 1, 2, 3, 3]


@pytest.mark.parametrize("sort", ALGORITHMS)
def test_negative_numbers(sort: SortFn[int]) -> None:
    assert sort([3, -1, -5, 0, 2]) == [-5, -1, 0, 2, 3]


@pytest.mark.parametrize("sort", ALGORITHMS_FLOAT)
def test_floats(sort: SortFn[float]) -> None:
    assert sort([3.5, -1.2, 0.0, 2.25]) == [-1.2, 0.0, 2.25, 3.5]


@pytest.mark.parametrize("sort", ALGORITHMS_STR)
def test_strings(sort: SortFn[str]) -> None:
    assert sort(["banana", "apple", "cherry"]) == ["apple", "banana", "cherry"]


@pytest.mark.parametrize("sort", ALGORITHMS)
def test_does_not_modify_the_input(sort: SortFn[int]) -> None:
    original = [3, 1, 2]
    before = list(original)
    sort(original)
    assert original == before


@pytest.mark.parametrize("sort", ALGORITHMS)
def test_return_value_is_a_new_list_not_the_same_object(sort: SortFn[int]) -> None:
    original = [3, 1, 2]
    assert sort(original) is not original


@pytest.mark.parametrize("sort", ALGORITHMS)
@pytest.mark.parametrize("seed", range(30))
def test_matches_python_builtin_sorted_on_random_lists(sort: SortFn[int], seed: int) -> None:
    rng = random.Random(seed)
    values = [rng.randint(-1000, 1000) for _ in range(rng.randint(0, 200))]
    assert sort(values) == sorted(values)


@pytest.mark.parametrize("sort", ALGORITHMS)
@pytest.mark.parametrize("seed", range(10))
def test_matches_sorted_on_lists_with_many_repeats(sort: SortFn[int], seed: int) -> None:
    # Only a handful of distinct values, so every algorithm's tie-handling
    # (duplicates, the `equal` bucket in quick sort, etc.) gets exercised hard.
    rng = random.Random(seed)
    values = [rng.randint(0, 3) for _ in range(rng.randint(0, 200))]
    assert sort(values) == sorted(values)
