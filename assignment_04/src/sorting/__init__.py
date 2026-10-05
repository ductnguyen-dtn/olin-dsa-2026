"""Four sorting algorithms, each returning a new sorted list without
modifying its input: insertion sort (Θ(n²)), merge sort (Θ(n log n) always),
quick sort (Θ(n log n) average, randomized pivot), and heap sort
(Θ(n log n) always, Θ(1) extra space). See each module's docstring for the
complexity analysis, and ``docs/complexity_analysis.md`` for the summary."""

from sorting.heap_sort import heap_sort
from sorting.insertion_sort import insertion_sort
from sorting.merge_sort import merge_sort
from sorting.quick_sort import quick_sort

__all__ = ["heap_sort", "insertion_sort", "merge_sort", "quick_sort"]
