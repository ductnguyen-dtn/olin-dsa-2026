"""Tests for meeting-conflict detection.

Both implementations must agree on every input, so most tests are
parametrised over the pair ``(has_conflict_naive, has_conflict_sorted)`` and the
pair of ``find_all_*`` functions.
"""

from __future__ import annotations

import random

import pytest

from meeting_scheduler import (
    Meeting,
    find_all_conflicts_naive,
    find_all_conflicts_sorted,
    has_conflict_naive,
    has_conflict_sorted,
    meetings_overlap,
)

HAS_CONFLICT_IMPLS = (has_conflict_naive, has_conflict_sorted)
FIND_CONFLICT_IMPLS = (find_all_conflicts_naive, find_all_conflicts_sorted)


def _pair_key(pair) -> tuple[object, ...]:
    """Canonical, order-independent key for a ConflictPair, for set comparison."""
    a, b = sorted([pair.first, pair.second])
    return (a.start, a.end, a.label, b.start, b.end, b.label)


# --------------------------------------------------------------------------- #
# Meeting construction
# --------------------------------------------------------------------------- #

def test_meeting_rejects_end_before_start() -> None:
    with pytest.raises(ValueError):
        Meeting(start=10, end=5, label="backwards")


def test_meeting_rejects_zero_length() -> None:
    with pytest.raises(ValueError):
        Meeting(start=5, end=5, label="instant")


# --------------------------------------------------------------------------- #
# Edge case: adjacent endpoints (the one the assignment calls out)
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("has_conflict", HAS_CONFLICT_IMPLS)
def test_adjacent_meetings_do_not_conflict(has_conflict) -> None:
    back_to_back = [
        Meeting(9_00, 10_00, "standup"),
        Meeting(10_00, 11_00, "review"),
        Meeting(11_00, 12_00, "lunch"),
    ]
    assert has_conflict(back_to_back) is False


@pytest.mark.parametrize("has_conflict", HAS_CONFLICT_IMPLS)
def test_one_minute_overlap_conflicts(has_conflict) -> None:
    assert has_conflict([Meeting(9_00, 10_01, "a"), Meeting(10_00, 11_00, "b")]) is True


def test_adjacent_endpoints_report_no_conflicting_pairs() -> None:
    meetings = [Meeting(0, 5, "a"), Meeting(5, 10, "b"), Meeting(10, 15, "c")]
    assert find_all_conflicts_naive(meetings) == []
    assert find_all_conflicts_sorted(meetings) == []


# --------------------------------------------------------------------------- #
# Empty / singleton / trivial collections
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("has_conflict", HAS_CONFLICT_IMPLS)
@pytest.mark.parametrize("meetings", [[], [Meeting(0, 1, "solo")]])
def test_no_conflict_when_fewer_than_two_meetings(has_conflict, meetings) -> None:
    assert has_conflict(meetings) is False


@pytest.mark.parametrize("find_conflicts", FIND_CONFLICT_IMPLS)
def test_find_conflicts_empty_for_trivial_inputs(find_conflicts) -> None:
    assert find_conflicts([]) == []
    assert find_conflicts([Meeting(0, 100, "solo")]) == []


# --------------------------------------------------------------------------- #
# Overlap shapes
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("has_conflict", HAS_CONFLICT_IMPLS)
def test_fully_contained_meeting_conflicts(has_conflict) -> None:
    assert has_conflict([Meeting(9, 17, "workday"), Meeting(12, 13, "lunch call")]) is True


@pytest.mark.parametrize("has_conflict", HAS_CONFLICT_IMPLS)
def test_identical_meetings_conflict(has_conflict) -> None:
    assert has_conflict([Meeting(9, 10, "a"), Meeting(9, 10, "b")]) is True


@pytest.mark.parametrize("has_conflict", HAS_CONFLICT_IMPLS)
def test_unsorted_input_still_detected(has_conflict) -> None:
    meetings = [
        Meeting(15, 16, "late"),
        Meeting(9, 12, "long morning"),
        Meeting(11, 11.5, "overlaps morning"),
        Meeting(13, 14, "afternoon"),
    ]
    assert has_conflict(meetings) is True


@pytest.mark.parametrize("has_conflict", HAS_CONFLICT_IMPLS)
def test_conflict_between_first_and_last_meeting(has_conflict) -> None:
    # First meeting spans the whole day; a scan that only compares neighbours
    # would miss this.
    meetings = [
        Meeting(0, 100, "all day"),
        Meeting(20, 21, "x"),
        Meeting(40, 41, "y"),
        Meeting(99, 101, "clips the end"),
    ]
    assert has_conflict(meetings) is True


# --------------------------------------------------------------------------- #
# find_all_conflicts: exact pair sets
# --------------------------------------------------------------------------- #

def test_find_all_conflicts_exact_set() -> None:
    meetings = [
        Meeting(0, 10, "A"),
        Meeting(5, 15, "B"),   # overlaps A
        Meeting(12, 20, "C"),  # overlaps B
        Meeting(30, 40, "D"),  # overlaps nobody
    ]
    expected = {
        _pair_key_from(meetings[0], meetings[1]),
        _pair_key_from(meetings[1], meetings[2]),
    }
    for find_conflicts in FIND_CONFLICT_IMPLS:
        got = {_pair_key(p) for p in find_conflicts(meetings)}
        assert got == expected, find_conflicts.__name__


def test_find_all_conflicts_all_overlap() -> None:
    # n meetings all sharing a common instant -> n*(n-1)/2 pairs.
    n = 6
    meetings = [Meeting(0, 100 + i, f"m{i}") for i in range(n)]
    for find_conflicts in FIND_CONFLICT_IMPLS:
        assert len(find_conflicts(meetings)) == n * (n - 1) // 2


def _pair_key_from(a: Meeting, b: Meeting) -> tuple[object, ...]:
    lo, hi = sorted([a, b])
    return (lo.start, lo.end, lo.label, hi.start, hi.end, hi.label)


# --------------------------------------------------------------------------- #
# Randomised cross-check: naive vs sorted must always agree
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("seed", range(50))
def test_naive_and_sorted_agree_random(seed: int) -> None:
    rng = random.Random(seed)
    meetings = []
    for i in range(rng.randint(0, 12)):
        start = rng.randint(0, 20)
        end = start + rng.randint(1, 8)
        meetings.append(Meeting(start, end, f"m{i}"))

    assert has_conflict_naive(meetings) == has_conflict_sorted(meetings)

    naive_pairs = {_pair_key(p) for p in find_all_conflicts_naive(meetings)}
    sorted_pairs = {_pair_key(p) for p in find_all_conflicts_sorted(meetings)}
    assert naive_pairs == sorted_pairs


# --------------------------------------------------------------------------- #
# meetings_overlap primitive
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Meeting(0, 10), Meeting(10, 20), False),  # adjacent
        (Meeting(0, 10), Meeting(9, 20), True),    # 1-unit overlap
        (Meeting(0, 10), Meeting(0, 10), True),    # identical
        (Meeting(0, 10), Meeting(3, 4), True),     # contained
        (Meeting(0, 10), Meeting(11, 12), False),  # disjoint
    ],
)
def test_meetings_overlap_primitive(a: Meeting, b: Meeting, expected: bool) -> None:
    assert meetings_overlap(a, b) is expected
    assert meetings_overlap(b, a) is expected  # symmetric
