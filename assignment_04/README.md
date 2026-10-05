# Olin DSA 2026: Assignment 4, Sorting Algorithms

Language: Python with type hints (`mypy --strict`).

## Contents

| Path | Component |
|---|---|
| [`src/sorting/insertion_sort.py`](src/sorting/insertion_sort.py) | Insertion sort, Θ(n²) |
| [`src/sorting/merge_sort.py`](src/sorting/merge_sort.py) | Merge sort, Θ(n log n) always, stable |
| [`src/sorting/quick_sort.py`](src/sorting/quick_sort.py) | Quick sort, randomized pivot, Θ(n log n) average |
| [`src/sorting/heap_sort.py`](src/sorting/heap_sort.py) | Heap sort, Θ(n log n) always, Θ(1) extra space |
| [`src/sorting/benchmark.py`](src/sorting/benchmark.py) | Benchmark script: runs all four, writes CSVs + a plot |
| [`tests/`](tests/) | pytest suite (214 tests) |
| [`docs/complexity_analysis.md`](docs/complexity_analysis.md) | Θ analysis for each of the four algorithms |
| [`docs/benchmarking.md`](docs/benchmarking.md) | Methodology, results, and conclusions from a real benchmark run |
| [`docs/frontiers_in_sorting.md`](docs/frontiers_in_sorting.md) | Extra credit: AlphaDev |
| [`docs/master_theorem.md`](docs/master_theorem.md) | Extra credit: the MIT 6.046 worksheet, all 25 problems |
| [`benchmark_data/`](benchmark_data/) | Real output from the benchmark script: `results.csv`, `summary.csv`, `runtime_vs_size.png` |

## Running

```bash
make venv     # one-time: create .venv, install pytest + mypy
make check    # pytest + mypy

# re-run the benchmark (a couple of minutes; writes into benchmark_data/)
.venv/bin/pip install matplotlib
PYTHONPATH=src .venv/bin/python -m sorting.benchmark
```

> This machine sources ROS 2 Jazzy in `.bashrc`, which puts `/opt/ros` on
> `PYTHONPATH` and breaks bare `pytest`. The Makefile runs everything in a
> clean environment.

## Design notes

All four algorithms share one interface, `fn(items: list[T]) -> list[T]`:
return a new sorted list, leave the input alone. That's what lets
`tests/test_sorting.py` test every shared property (correctness against
`sorted()`, edge cases, "input untouched") once, parametrized over all four,
instead of four times over. `tests/test_stability.py` covers the one property
that is not shared: insertion sort and merge sort are stable, quick sort and
heap sort are not guaranteed to be.

Every comparison in every algorithm is written using only `__lt__` (see
`src/sorting/_comparable.py`), so any type that defines just that one method
is sortable here, the same way `sorted()` and `list.sort()` work in Python.

## AI assistance

The code, its docstrings and inline comments, and the writeups in `docs/`
were produced with the help of Claude (Anthropic), under my direction and
review.
