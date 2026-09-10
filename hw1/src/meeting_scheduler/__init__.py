"""Meeting-conflict detection: a naive O(n^2) check and a sorted O(n log n) check.

See ``docs/meeting_scheduler_analysis.md`` for the runtime discussion.
"""

from meeting_scheduler.scheduler import (
    Meeting,
    ConflictPair,
    find_all_conflicts_naive,
    find_all_conflicts_sorted,
    has_conflict_naive,
    has_conflict_sorted,
    meetings_overlap,
)

__all__ = [
    "Meeting",
    "ConflictPair",
    "find_all_conflicts_naive",
    "find_all_conflicts_sorted",
    "has_conflict_naive",
    "has_conflict_sorted",
    "meetings_overlap",
]
