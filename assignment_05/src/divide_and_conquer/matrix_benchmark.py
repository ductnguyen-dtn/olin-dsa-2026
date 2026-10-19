"""Benchmark conventional vs. Strassen matrix multiplication, and sweep the
hybrid threshold to find where Strassen stops being worth it.

Run with (from the assignment_05 directory, with the venv active)::

    PYTHONPATH=src python -m divide_and_conquer.matrix_benchmark

Writes benchmark_data/algorithm_results.csv (conventional vs. pure Strassen
across sizes), benchmark_data/threshold_results.csv (Strassen at a fixed
size across hybrid thresholds), and, if matplotlib is installed, two plots.
See docs/strassen_analysis.md for the methodology and conclusions drawn
from a real run's output.
"""

from __future__ import annotations

import csv
import random
import statistics
import time
from pathlib import Path
from typing import TypedDict

from divide_and_conquer.matrix import Matrix

TRIALS = 3

# Pure Strassen (threshold=1) recurses all the way to 1x1 scalar products,
# which means n^log2(7) ~= n^2.807 leaf-level Python function calls. That
# grows fast enough that sizes above ~128 take too long to be worth
# benchmarking here; the hybrid sweep below covers larger sizes instead,
# using thresholds that keep the recursion shallow.
ALGORITHM_SIZES = [2, 4, 8, 16, 32, 64, 128]

# Fixed size for the threshold sweep: large enough that recursing matters,
# small enough that even threshold=1 finishes in reasonable time.
THRESHOLD_SWEEP_SIZE = 128
THRESHOLDS = [1, 2, 4, 8, 16, 32, 64, 128]


class AlgorithmRow(TypedDict):
    algorithm: str
    size: int
    trial: int
    seconds: float


class ThresholdRow(TypedDict):
    threshold: int
    size: int
    trial: int
    seconds: float


def _random_matrix(n: int, rng: random.Random) -> Matrix:
    data = [[rng.uniform(-10, 10) for _ in range(n)] for _ in range(n)]
    return Matrix(n, data)


def run_algorithm_comparison(output_dir: Path) -> list[AlgorithmRow]:
    """Conventional multiply vs. pure Strassen (threshold=1) across sizes."""
    rng = random.Random(0)
    rows: list[AlgorithmRow] = []

    for n in ALGORITHM_SIZES:
        a = _random_matrix(n, rng)
        b = _random_matrix(n, rng)

        for trial in range(TRIALS):
            start = time.perf_counter()
            a.multiply(b)
            elapsed = time.perf_counter() - start
            rows.append(AlgorithmRow(algorithm="conventional", size=n, trial=trial, seconds=elapsed))
            print(f"conventional  n={n:>4}  trial {trial + 1}/{TRIALS}  {elapsed:.6f}s")

        for trial in range(TRIALS):
            start = time.perf_counter()
            a.strassen_multiply(b, threshold=1)
            elapsed = time.perf_counter() - start
            rows.append(AlgorithmRow(algorithm="strassen", size=n, trial=trial, seconds=elapsed))
            print(f"strassen      n={n:>4}  trial {trial + 1}/{TRIALS}  {elapsed:.6f}s")

    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "algorithm_results.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["algorithm", "size", "trial", "seconds"])
        writer.writeheader()
        writer.writerows(rows)

    return rows


def run_threshold_sweep(output_dir: Path) -> list[ThresholdRow]:
    """Strassen at a fixed size, across hybrid thresholds, to find the
    apparent optimal switch-over point between Strassen and conventional
    multiplication."""
    rng = random.Random(1)
    a = _random_matrix(THRESHOLD_SWEEP_SIZE, rng)
    b = _random_matrix(THRESHOLD_SWEEP_SIZE, rng)
    rows: list[ThresholdRow] = []

    for threshold in THRESHOLDS:
        for trial in range(TRIALS):
            start = time.perf_counter()
            a.strassen_multiply(b, threshold=threshold)
            elapsed = time.perf_counter() - start
            rows.append(
                ThresholdRow(
                    threshold=threshold, size=THRESHOLD_SWEEP_SIZE, trial=trial, seconds=elapsed
                )
            )
            print(f"threshold={threshold:>4}  n={THRESHOLD_SWEEP_SIZE}  trial {trial + 1}/{TRIALS}  {elapsed:.6f}s")

    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "threshold_results.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["threshold", "size", "trial", "seconds"])
        writer.writeheader()
        writer.writerows(rows)

    return rows


def _mean_by_key(rows: list[dict[str, float]], key: str, value_key: str = "seconds") -> dict[float, float]:
    groups: dict[float, list[float]] = {}
    for row in rows:
        groups.setdefault(row[key], []).append(row[value_key])
    return {k: statistics.mean(v) for k, v in groups.items()}


def plot_algorithm_comparison(rows: list[AlgorithmRow], output_dir: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping plots (the CSVs still have the data).")
        return

    by_algorithm: dict[str, dict[int, list[float]]] = {}
    for row in rows:
        by_algorithm.setdefault(row["algorithm"], {}).setdefault(row["size"], []).append(row["seconds"])

    fig, ax = plt.subplots(figsize=(7, 5))
    for name, by_size in sorted(by_algorithm.items()):
        sizes = sorted(by_size)
        times = [statistics.mean(by_size[s]) for s in sizes]
        ax.plot(sizes, times, marker="o", label=name)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("matrix size (n)")
    ax.set_ylabel("mean runtime (seconds)")
    ax.set_title("Conventional vs. pure Strassen multiplication (log-log)")
    ax.legend()
    ax.grid(True, which="both", linestyle=":", linewidth=0.5)
    fig.tight_layout()
    fig.savefig(output_dir / "algorithm_comparison.png", dpi=150)
    print(f"Wrote {output_dir / 'algorithm_comparison.png'}")


def plot_threshold_sweep(rows: list[ThresholdRow], output_dir: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping plots (the CSVs still have the data).")
        return

    by_threshold: dict[int, list[float]] = {}
    for row in rows:
        by_threshold.setdefault(row["threshold"], []).append(row["seconds"])

    thresholds = sorted(by_threshold)
    times = [statistics.mean(by_threshold[t]) for t in thresholds]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(thresholds, times, marker="o")
    ax.set_xscale("log")
    ax.set_xlabel(f"hybrid threshold (base-case block size, n={THRESHOLD_SWEEP_SIZE})")
    ax.set_ylabel("mean runtime (seconds)")
    ax.set_title("Hybrid Strassen/conventional threshold sweep")
    ax.grid(True, which="both", linestyle=":", linewidth=0.5)
    fig.tight_layout()
    fig.savefig(output_dir / "threshold_sweep.png", dpi=150)
    print(f"Wrote {output_dir / 'threshold_sweep.png'}")


def main() -> None:
    output_dir = Path(__file__).resolve().parents[2] / "benchmark_data"
    algorithm_rows = run_algorithm_comparison(output_dir)
    plot_algorithm_comparison(algorithm_rows, output_dir)
    threshold_rows = run_threshold_sweep(output_dir)
    plot_threshold_sweep(threshold_rows, output_dir)


if __name__ == "__main__":
    main()
