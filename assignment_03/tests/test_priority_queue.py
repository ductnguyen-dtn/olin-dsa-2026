"""Tests for MinPriorityQueue, covering every function in the interface."""

from __future__ import annotations

import random

import pytest

from graph_search import MinPriorityQueue


def test_new_queue_is_empty() -> None:
    q: MinPriorityQueue[str] = MinPriorityQueue()
    assert q.is_empty() is True
    assert len(q) == 0


def test_next_on_empty_returns_none() -> None:
    q: MinPriorityQueue[str] = MinPriorityQueue()
    assert q.next() is None


def test_add_makes_queue_non_empty() -> None:
    q: MinPriorityQueue[str] = MinPriorityQueue()
    q.add_with_priority("a", 1.0)
    assert q.is_empty() is False
    assert "a" in q


def test_next_returns_lowest_priority_value_first() -> None:
    q: MinPriorityQueue[str] = MinPriorityQueue()
    q.add_with_priority("low-urgency", 10.0)
    q.add_with_priority("urgent", 1.0)
    q.add_with_priority("medium", 5.0)
    assert q.next() == "urgent"
    assert q.next() == "medium"
    assert q.next() == "low-urgency"
    assert q.next() is None
    assert q.is_empty() is True


def test_next_removes_the_element() -> None:
    q: MinPriorityQueue[str] = MinPriorityQueue()
    q.add_with_priority("a", 1.0)
    q.next()
    assert "a" not in q
    assert len(q) == 0


def test_adjust_priority_to_lower_moves_element_earlier() -> None:
    q: MinPriorityQueue[str] = MinPriorityQueue()
    q.add_with_priority("a", 1.0)
    q.add_with_priority("b", 2.0)
    q.add_with_priority("c", 3.0)
    q.adjust_priority("c", 0.0)
    assert q.next() == "c"


def test_adjust_priority_to_higher_moves_element_later() -> None:
    q: MinPriorityQueue[str] = MinPriorityQueue()
    q.add_with_priority("a", 1.0)
    q.add_with_priority("b", 2.0)
    q.adjust_priority("a", 100.0)
    assert q.next() == "b"
    assert q.next() == "a"


def test_adjust_priority_of_missing_element_raises() -> None:
    q: MinPriorityQueue[str] = MinPriorityQueue()
    with pytest.raises(KeyError):
        q.adjust_priority("missing", 1.0)


def test_adding_an_existing_element_updates_it_instead_of_duplicating() -> None:
    q: MinPriorityQueue[str] = MinPriorityQueue()
    q.add_with_priority("a", 5.0)
    q.add_with_priority("b", 3.0)
    q.add_with_priority("a", 1.0)
    assert len(q) == 2
    assert q.next() == "a"
    assert q.next() == "b"
    assert q.next() is None


def test_negative_and_zero_priorities() -> None:
    q: MinPriorityQueue[str] = MinPriorityQueue()
    q.add_with_priority("zero", 0.0)
    q.add_with_priority("negative", -5.0)
    q.add_with_priority("positive", 5.0)
    assert [q.next(), q.next(), q.next()] == ["negative", "zero", "positive"]


def test_works_with_tuple_elements() -> None:
    q: MinPriorityQueue[tuple[int, int]] = MinPriorityQueue()
    q.add_with_priority((1, 1), 2.0)
    q.add_with_priority((0, 0), 1.0)
    assert q.next() == (0, 0)


@pytest.mark.parametrize("seed", range(30))
def test_drains_in_sorted_order_after_random_adjustments(seed: int) -> None:
    rng = random.Random(seed)
    q: MinPriorityQueue[int] = MinPriorityQueue()
    priorities: dict[int, float] = {}

    for item in range(rng.randint(0, 40)):
        priorities[item] = float(rng.randint(0, 100))
        q.add_with_priority(item, priorities[item])
    for item in list(priorities):
        if rng.random() < 0.5:
            priorities[item] = float(rng.randint(0, 100))
            q.adjust_priority(item, priorities[item])

    drained = []
    while not q.is_empty():
        popped = q.next()
        assert popped is not None
        drained.append(priorities[popped])
    assert drained == sorted(priorities.values())
