"""Tests for MinHeap.

The randomized tests check the heap against a plain dict used as an oracle: the
smallest priority in the dict is what the heap must return next.
"""

from __future__ import annotations

import math
import random

import pytest

from graph_search import MinHeap


def _assert_valid(heap: MinHeap[int]) -> None:
    """Check the heap property and that the item->position index is in sync,
    by reaching into the internals."""
    entries = heap._entries
    assert len(heap._index) == len(entries)
    for position, (priority, item) in enumerate(entries):
        assert heap._index[item] == position
        if position > 0:
            assert entries[(position - 1) // 2][0] <= priority


def test_new_heap_is_empty() -> None:
    heap: MinHeap[str] = MinHeap()
    assert heap.is_empty() is True
    assert len(heap) == 0


def test_pop_and_peek_on_empty_return_none() -> None:
    heap: MinHeap[str] = MinHeap()
    assert heap.pop() is None
    assert heap.peek() is None


def test_push_makes_heap_non_empty() -> None:
    heap: MinHeap[str] = MinHeap()
    heap.push("a", 1.0)
    assert heap.is_empty() is False
    assert len(heap) == 1
    assert "a" in heap


def test_peek_returns_minimum_without_removing() -> None:
    heap: MinHeap[str] = MinHeap()
    heap.push("b", 2.0)
    heap.push("a", 1.0)
    heap.push("c", 3.0)
    assert heap.peek() == ("a", 1.0)
    assert len(heap) == 3


def test_pop_returns_items_in_priority_order() -> None:
    heap: MinHeap[str] = MinHeap()
    for item, priority in [("d", 4.0), ("b", 2.0), ("a", 1.0), ("c", 3.0)]:
        heap.push(item, priority)
    assert [heap.pop() for _ in range(4)] == [("a", 1.0), ("b", 2.0), ("c", 3.0), ("d", 4.0)]
    assert heap.is_empty() is True


def test_pop_removes_the_item_from_membership() -> None:
    heap: MinHeap[str] = MinHeap()
    heap.push("a", 1.0)
    heap.pop()
    assert "a" not in heap


def test_equal_priorities_are_all_returned() -> None:
    heap: MinHeap[str] = MinHeap()
    for item in "abc":
        heap.push(item, 1.0)
    assert {heap.pop()[0] for _ in range(3)} == {"a", "b", "c"}  # type: ignore[index]


def test_pushing_a_duplicate_item_is_rejected() -> None:
    heap: MinHeap[str] = MinHeap()
    heap.push("a", 1.0)
    with pytest.raises(ValueError):
        heap.push("a", 2.0)
    assert heap.priority_of("a") == 1.0


def test_nan_priority_is_rejected() -> None:
    heap: MinHeap[str] = MinHeap()
    with pytest.raises(ValueError):
        heap.push("a", math.nan)
    heap.push("b", 1.0)
    with pytest.raises(ValueError):
        heap.update("b", math.nan)


def test_priority_of() -> None:
    heap: MinHeap[str] = MinHeap()
    heap.push("a", 7.5)
    assert heap.priority_of("a") == 7.5
    with pytest.raises(KeyError):
        heap.priority_of("missing")


def test_update_to_lower_priority_moves_item_forward() -> None:
    heap: MinHeap[str] = MinHeap()
    heap.push("a", 1.0)
    heap.push("b", 2.0)
    heap.push("c", 3.0)
    heap.update("c", 0.5)
    assert heap.pop() == ("c", 0.5)


def test_update_to_higher_priority_moves_item_back() -> None:
    heap: MinHeap[str] = MinHeap()
    heap.push("a", 1.0)
    heap.push("b", 2.0)
    heap.push("c", 3.0)
    heap.update("a", 10.0)
    assert [heap.pop() for _ in range(3)] == [("b", 2.0), ("c", 3.0), ("a", 10.0)]


def test_update_to_the_same_priority_changes_nothing() -> None:
    heap: MinHeap[str] = MinHeap()
    heap.push("a", 1.0)
    heap.push("b", 2.0)
    heap.update("b", 2.0)
    assert heap.pop() == ("a", 1.0)
    assert heap.pop() == ("b", 2.0)


def test_update_missing_item_raises() -> None:
    heap: MinHeap[str] = MinHeap()
    with pytest.raises(KeyError):
        heap.update("missing", 1.0)


def test_usable_again_after_being_emptied() -> None:
    heap: MinHeap[int] = MinHeap()
    heap.push(1, 1.0)
    heap.pop()
    heap.push(2, 5.0)
    assert heap.peek() == (2, 5.0)


@pytest.mark.parametrize("seed", range(50))
def test_matches_dict_oracle_for_random_operations(seed: int) -> None:
    rng = random.Random(seed)
    heap: MinHeap[int] = MinHeap()
    oracle: dict[int, float] = {}

    for _ in range(rng.randint(0, 150)):
        op = rng.choice(["push", "pop", "update", "peek"])
        if op == "push":
            item = rng.randint(0, 30)
            if item not in oracle:
                priority = float(rng.randint(0, 20))
                heap.push(item, priority)
                oracle[item] = priority
        elif op == "update" and oracle:
            item = rng.choice(list(oracle))
            priority = float(rng.randint(0, 20))
            heap.update(item, priority)
            oracle[item] = priority
        elif op == "pop":
            entry = heap.pop()
            if not oracle:
                assert entry is None
            else:
                assert entry is not None
                item, priority = entry
                # Ties can come out in any order, so check the priority is the
                # minimum and that the item really had that priority.
                assert priority == min(oracle.values())
                assert oracle.pop(item) == priority
        elif op == "peek":
            entry = heap.peek()
            if not oracle:
                assert entry is None
            else:
                assert entry is not None
                assert entry[1] == min(oracle.values())

        assert len(heap) == len(oracle)
        _assert_valid(heap)


@pytest.mark.parametrize("seed", range(20))
def test_heap_sort_gives_sorted_output(seed: int) -> None:
    rng = random.Random(seed)
    values = [rng.random() for _ in range(rng.randint(0, 200))]
    heap: MinHeap[int] = MinHeap()
    for i, v in enumerate(values):
        heap.push(i, v)
    popped = []
    while not heap.is_empty():
        entry = heap.pop()
        assert entry is not None
        popped.append(entry[1])
    assert popped == sorted(values)
