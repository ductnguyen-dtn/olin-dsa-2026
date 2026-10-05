"""Benchmark the four sorting algorithms across a range of list sizes.

Run with (from the ``assignment_04`` directory, with the venv active)::

    PYTHONPATH=src python -m sorting.benchmark

Writes ``benchmark_data/results.csv`` (one row per trial),
``benchmark_data/summary.csv`` (one row per algorithm/size, mean and standard
deviation), and, if matplotlib is installed, a log-log plot at
``benchmark_data/runtime_vs_size.png``. See ``docs/benchmarking.md`` for the
methodology writeup and conclusions drawn from a real run's output.
"""

from __future__ import annotations

import csv
import random
import statistics
import time
from pathlib import Path
from typing import Callable, TypedDict, cast

from sorting import heap_sort, insertion_sort, merge_sort, quick_sort


class TrialRow(TypedDict):
    algorithm: str
    size: int
    trial: int
    seconds: float


class SummaryRow(TypedDict):
    algorithm: str
    size: int
    trials: int
    mean_seconds: float
    stdev_seconds: float

# Each sort function is generic (Callable[[list[T]], list[T]]); this module
# only ever sorts ints, so the cast just pins T = int for mypy's benefit.
ALGORITHMS: dict[str, Callable[[list[int]], list[int]]] = {
    "insertion_sort": cast(Callable[[list[int]], list[int]], insertion_sort),
    "merge_sort": cast(Callable[[list[int]], list[int]], merge_sort),
    "quick_sort": cast(Callable[[list[int]], list[int]], quick_sort),
    "heap_sort": cast(Callable[[list[int]], list[int]], heap_sort),
}

# insertion_sort is Θ(n²); past a few thousand elements it is too slow to be
# worth waiting for, so it only runs at the smaller sizes.
QUADRATIC_SIZES = [10, 50, 100, 500, 1_000, 2_000, 5_000, 10_000]
LINEARITHMIC_SIZES = QUADRATIC_SIZES + [20_000, 50_000, 100_000, 200_000]

TRIALS = 5


def _random_list(size: int, rng: random.Random) -> list[int]:
    """A list of ``size`` random integers. The range scales with size so
    larger lists are not mostly duplicate values, without caring about exact
    uniqueness."""
    upper = max(1000, size * 10)
    return [rng.randint(0, upper) for _ in range(size)]


def run(output_dir: Path) -> list[SummaryRow]:
    """Run every algorithm at every size it supports, ``TRIALS`` times each,
    writing ``results.csv`` and ``summary.csv`` into ``output_dir``.

    Returns the summary rows (also what gets written to ``summary.csv``), so
    the caller can plot them without re-reading the file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(0)  # fixed seed: reruns are comparable, not cherry-picked

    raw_rows: list[TrialRow] = []
    for name, sort_fn in ALGORITHMS.items():
        sizes = QUADRATIC_SIZES if name == "insertion_sort" else LINEARITHMIC_SIZES
        for size in sizes:
            for trial in range(TRIALS):
                values = _random_list(size, rng)
                start = time.perf_counter()
                sort_fn(values)
                elapsed = time.perf_counter() - start
                raw_rows.append(
                    TrialRow(algorithm=name, size=size, trial=trial, seconds=elapsed)
                )
                print(f"{name:>15}  n={size:>7}  trial {trial + 1}/{TRIALS}  {elapsed:.4f}s")

    with (output_dir / "results.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["algorithm", "size", "trial", "seconds"])
        writer.writeheader()
        writer.writerows(raw_rows)

    summary_rows = _summarize(raw_rows)
    with (output_dir / "summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["algorithm", "size", "trials", "mean_seconds", "stdev_seconds"]
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    return summary_rows


def _summarize(raw_rows: list[TrialRow]) -> list[SummaryRow]:
    """Group ``raw_rows`` by (algorithm, size) and compute mean/stdev runtime."""
    groups: dict[tuple[str, int], list[float]] = {}
    for row in raw_rows:
        key = (row["algorithm"], row["size"])
        groups.setdefault(key, []).append(row["seconds"])

    summary: list[SummaryRow] = []
    for (name, size), times in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        summary.append(
            SummaryRow(
                algorithm=name,
                size=size,
                trials=len(times),
                mean_seconds=statistics.mean(times),
                stdev_seconds=statistics.stdev(times) if len(times) > 1 else 0.0,
            )
        )
    return summary


def plot(summary_rows: list[SummaryRow], output_dir: Path) -> None:
    """Save a log-log runtime-vs-size plot to ``output_dir``. Skips silently
    if matplotlib is not installed, since the CSVs are the real data and the
    plot is just a visualization of them."""
    try:
        import matplotlib

        matplotlib.use("Agg")  # no display needed, this just saves a file
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping the plot (the CSVs still have the data).")
        return

    by_algorithm: dict[str, list[tuple[int, float]]] = {}
    for row in summary_rows:
        by_algorithm.setdefault(row["algorithm"], []).append((row["size"], row["mean_seconds"]))

    fig, ax = plt.subplots(figsize=(7, 5))
    for name, points in sorted(by_algorithm.items()):
        points.sort()
        sizes = [p[0] for p in points]
        times = [p[1] for p in points]
        ax.plot(sizes, times, marker="o", label=name)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("list size (n)")
    ax.set_ylabel("mean runtime (seconds)")
    ax.set_title("Sorting algorithm runtime vs. input size (log-log)")
    ax.legend()
    ax.grid(True, which="both", linestyle=":", linewidth=0.5)
    fig.tight_layout()
    fig.savefig(output_dir / "runtime_vs_size.png", dpi=150)
    print(f"Wrote {output_dir / 'runtime_vs_size.png'}")


def main() -> None:
    output_dir = Path(__file__).resolve().parents[2] / "benchmark_data"
    summary_rows = run(output_dir)
    plot(summary_rows, output_dir)


if __name__ == "__main__":
    main()
