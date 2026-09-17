# Meeting Scheduler — Runtime Analysis

Code: [`src/meeting_scheduler/scheduler.py`](../src/meeting_scheduler/scheduler.py)
Tests: [`tests/test_meeting_scheduler.py`](../tests/test_meeting_scheduler.py)

The task: given a collection of `n` meetings, decide whether any two of them
overlap in time (and, in the `find_all_*` variants, list every overlapping
pair). Two meetings overlap when each starts strictly before the other ends;
meetings that merely touch at an endpoint (`a.end == b.start`) do **not**
overlap.

```python
def meetings_overlap(a, b):
    return a.start < b.end and b.start < a.end   # strict '<' => adjacent is OK
```

---

## Approach 1 — naive all-pairs check

`has_conflict_naive` / `find_all_conflicts_naive`

Compare every meeting against every later meeting:

```
for i in 0 .. n-1:
    for j in i+1 .. n-1:
        if meetings_overlap(items[i], items[j]): ...
```

The number of pairs is `n*(n-1)/2`, and `meetings_overlap` is `O(1)`.

| | growth |
|---|---|
| `find_all_conflicts_naive` (must inspect every pair) | **Θ(n²)** always |
| `has_conflict_naive` (stops at first conflict) | **O(n²)** worst case, **O(1)** best case (first two meetings clash) |
| extra space | **O(1)** beyond the returned list |

If the input size doubles, the work roughly **quadruples**. At `n = 1,000`
that is ~500,000 comparisons; at `n = 100,000` it is ~5 billion — the point
where this approach stops being usable.

---

## Approach 2 — sort first, then sweep

`has_conflict_sorted` / `find_all_conflicts_sorted`

Sort the meetings by start time (Python's built-in `sorted`, Timsort,
`O(n log n)`). Once sorted, all the meetings that could overlap a given meeting
are contiguous — you no longer have to look backwards past a meeting that has
already ended.

**Existence check** (`has_conflict_sorted`): walk the sorted list tracking the
largest `end` seen so far. If the current meeting starts before that maximum
end, some earlier meeting is still running → conflict.

```
sort by start                       O(n log n)
scan once, keep running max end     O(n)
```

| | growth |
|---|---|
| `has_conflict_sorted` | **O(n log n)** (dominated by the sort) |
| extra space | **O(n)** for the sorted copy |

**Listing all pairs** (`find_all_conflicts_sorted`): walk the sorted list
keeping a set of still-open meetings (those whose `end` is after the current
start). Every open meeting overlaps the current one, so emit those pairs, then
add the current meeting to the open set. A meeting leaves the open set as soon
as it can never conflict again.

```
sort by start                       O(n log n)
sweep, pruning the open set         O(n + k)   k = number of overlapping pairs
```

| | growth |
|---|---|
| `find_all_conflicts_sorted` | **O(n log n + k)** |
| extra space | **O(n)** sorted copy + open set |

`k` can be as large as `n*(n-1)/2` (imagine every meeting spanning the whole
day), and then you cannot beat Θ(n²) — you are forced to *write down* that many
pairs. But when conflicts are sparse (`k = O(n)`, the realistic calendar case)
the sorted sweep is `O(n log n)` overall while the naive version is still
`Θ(n²)`.

---

## Summary

| input shape | naive | sorted |
|---|---|---|
| "is there any conflict?", conflict exists early | O(1) | O(n log n) |
| "is there any conflict?", worst case | O(n²) | **O(n log n)** |
| "list all conflicts", sparse (`k ≈ n`) | O(n²) | **O(n log n)** |
| "list all conflicts", dense (`k ≈ n²`) | O(n²) | O(n²) — output-bound |

The sort costs `O(n log n)` up front but removes the quadratic factor from
every case except the one where the answer itself is quadratically large. For
`has_conflict`, the naive version can still win when a conflict is
near-guaranteed and cheap to find, which is why both are kept and cross-checked
against each other in the tests (`test_naive_and_sorted_agree_random`).
