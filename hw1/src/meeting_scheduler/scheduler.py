"""Detect scheduling conflicts within a collection of meetings.

Two meetings *conflict* when their time intervals overlap on more than a single
instant.  Meetings that merely touch at an endpoint (one ends exactly when the
next begins) do **not** conflict — that is the classic edge case, and it is
covered by the tests.

Interface
---------
* :func:`has_conflict_naive`  / :func:`has_conflict_sorted`
      ``bool`` — is there at least one conflict anywhere in the collection?
* :func:`find_all_conflicts_naive` / :func:`find_all_conflicts_sorted`
      the actual conflicting pairs.

The ``_naive`` and ``_sorted`` variants compute the same answers by different
strategies; see ``docs/meeting_scheduler_analysis.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, order=True)
class Meeting:
    """A half-open time interval ``[start, end)``.

    ``start`` and ``end`` are unitless numbers (minutes past midnight, POSIX
    seconds, whatever the caller uses) as long as they are mutually comparable.
    A meeting must have positive duration (``end > start``); a zero-length
    interval is empty under the half-open convention and is rejected rather
    than silently never conflicting.  Field order puts ``start`` first so the
    natural sort is by start time, then end time — exactly the order
    :func:`find_all_conflicts_sorted` relies on.
    """

    start: float
    end: float
    label: str = ""

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValueError(
                f"meeting {self.label!r} must end after it starts, "
                f"got start={self.start}, end={self.end}"
            )


@dataclass(frozen=True)
class ConflictPair:
    """Two meetings that overlap.  ``first`` is the earlier-starting meeting."""

    first: Meeting
    second: Meeting


def meetings_overlap(a: Meeting, b: Meeting) -> bool:
    """Return ``True`` when ``a`` and ``b`` share more than a single instant.

    Standard interval-overlap test: they overlap iff each one starts strictly
    before the other one ends.  Strict ``<`` is what makes adjacent meetings
    (``a.end == b.start``) count as non-conflicting.
    """
    return a.start < b.end and b.start < a.end


def find_all_conflicts_naive(meetings: Iterable[Meeting]) -> list[ConflictPair]:
    """Every conflicting pair, found by checking all pairs.

    Time:  O(n^2) comparisons (n * (n - 1) / 2 pairs).
    Space: O(1) beyond the output.
    """
    items = list(meetings)
    conflicts: list[ConflictPair] = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i], items[j]
            if meetings_overlap(a, b):
                first, second = (a, b) if a.start <= b.start else (b, a)
                conflicts.append(ConflictPair(first, second))
    return conflicts


def has_conflict_naive(meetings: Iterable[Meeting]) -> bool:
    """``True`` if any two meetings conflict. All-pairs scan, O(n^2) worst case.

    Returns as soon as the first conflict is found, so best case is O(1).
    """
    items = list(meetings)
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if meetings_overlap(items[i], items[j]):
                return True
    return False


def find_all_conflicts_sorted(meetings: Iterable[Meeting]) -> list[ConflictPair]:
    """Every conflicting pair, using a sort to avoid the all-pairs scan.

    Strategy: sort by start time.  Walk the sorted list keeping the meetings
    that are still "open" (end after the current meeting's start).  Any meeting
    still open when a new one starts overlaps it.  Because a meeting is dropped
    from the open set the moment it can no longer conflict, the inner work is
    proportional to the number of conflicts reported.

    Time:  O(n log n) for the sort, then O(n + k) for the sweep where ``k`` is
           the number of conflicting pairs. Worst case (everything overlaps
           everything) k = O(n^2) and the output itself is that big.
    Space: O(n) for the sorted copy and the open set.
    """
    ordered = sorted(meetings)  # by (start, end, label)
    conflicts: list[ConflictPair] = []
    open_meetings: list[Meeting] = []

    for current in ordered:
        # Drop meetings that finished at or before `current` starts. Strict `>`
        # keeps an adjacent meeting (prev.end == current.start) from counting.
        open_meetings = [m for m in open_meetings if m.end > current.start]
        for earlier in open_meetings:
            conflicts.append(ConflictPair(earlier, current))
        open_meetings.append(current)

    return conflicts


def has_conflict_sorted(meetings: Iterable[Meeting]) -> bool:
    """``True`` if any two meetings conflict, found via sorting.

    Sort by start time; then a conflict exists iff some meeting starts strictly
    before the previous meeting (by start order) ends.  Tracking the maximum end
    seen so far is enough.

    Time:  O(n log n) for the sort, O(n) for the scan.
    Space: O(n) for the sorted copy.
    """
    ordered = sorted(meetings)
    max_end_so_far: float | None = None
    for meeting in ordered:
        if max_end_so_far is not None and meeting.start < max_end_so_far:
            return True
        if max_end_so_far is None or meeting.end > max_end_so_far:
            max_end_so_far = meeting.end
    return False
