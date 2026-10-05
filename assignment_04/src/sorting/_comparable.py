"""Shared typing helper: anything orderable with ``<``, which is all these
sorting algorithms need (every comparison in every algorithm here is written
using only ``__lt__``, even where ``<=`` or ``>`` would read more naturally,
so that a type only has to define one method to be sortable)."""

from __future__ import annotations

from typing import Protocol, TypeVar


class Comparable(Protocol):
    def __lt__(self, other: object, /) -> bool: ...


T = TypeVar("T", bound=Comparable)
