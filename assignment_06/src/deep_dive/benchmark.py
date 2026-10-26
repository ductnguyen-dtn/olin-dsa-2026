"""Benchmark policy iteration vs. value iteration: outer-loop iteration
count and wall-clock time, across gridworld sizes and reward/noise setups.

Run with (from the assignment_06 directory, with the venv active)::

    PYTHONPATH=src python -m deep_dive.benchmark

Writes benchmark_data/mdp_results.csv and, if matplotlib is installed, a
plot of runtime and iteration count vs. grid size for both algorithms. See
docs/policy_vs_value_iteration.md for the methodology and the conclusions
drawn from a real run's output.
"""

from __future__ import annotations

import csv
import statistics
import time
from pathlib import Path
from typing import TypedDict

from deep_dive.dp import policy_iteration, value_iteration
from deep_dive.gridworld import GridWorld

TRIALS = 3
GAMMA = 0.95
THETA = 1e-6

# Grid sizes to sweep (n x n), holding reward setup fixed at the "standard"
# setup below. Policy iteration re-runs a full evaluation sweep to
# convergence on *every* outer iteration, so its cost grows much faster
# with grid size than value iteration's. 32x32 (1024 states) is already
# enough to show that gap clearly in a pure-Python implementation, without
# the sweep taking an impractically long time.
SIZES = [4, 8, 16, 32]

# Reward/noise setups to sweep, holding grid size fixed at STD_SIZE. Each is
# (label, step_reward, noise).
STD_SIZE = 16
REWARD_SETUPS = [
    ("standard", -0.04, 0.2),
    ("harsh_steps", -1.0, 0.2),
    ("no_noise", -0.04, 0.0),
    ("high_noise", -0.04, 0.4),
]


class ResultRow(TypedDict):
    sweep: str  # "size" or "reward_setup"
    label: str  # the size (as str) or the reward-setup name
    algorithm: str
    trial: int
    iterations: int
    seconds: float


def _make_grid(n: int, step_reward: float, noise: float) -> GridWorld:
    return GridWorld(rows=n, cols=n, terminals={(n - 1, n - 1): 1.0}, step_reward=step_reward, noise=noise)


def _time_one(mdp: GridWorld, algorithm: str) -> tuple[int, float]:
    solve = value_iteration if algorithm == "value_iteration" else policy_iteration
    start = time.perf_counter()
    _, _, iterations = solve(mdp, GAMMA, theta=THETA)
    elapsed = time.perf_counter() - start
    return iterations, elapsed


def run_size_sweep(output_dir: Path) -> list[ResultRow]:
    rows: list[ResultRow] = []
    for n in SIZES:
        mdp = _make_grid(n, step_reward=-0.04, noise=0.2)
        for algorithm in ("value_iteration", "policy_iteration"):
            for trial in range(TRIALS):
                iterations, seconds = _time_one(mdp, algorithm)
                rows.append(
                    ResultRow(
                        sweep="size", label=str(n), algorithm=algorithm,
                        trial=trial, iterations=iterations, seconds=seconds,
                    )
                )
                print(f"size n={n:>3}  {algorithm:<17} trial {trial + 1}/{TRIALS}  "
                      f"iters={iterations:>4}  {seconds:.6f}s")
    return rows


def run_reward_setup_sweep(output_dir: Path) -> list[ResultRow]:
    rows: list[ResultRow] = []
    for label, step_reward, noise in REWARD_SETUPS:
        mdp = _make_grid(STD_SIZE, step_reward=step_reward, noise=noise)
        for algorithm in ("value_iteration", "policy_iteration"):
            for trial in range(TRIALS):
                iterations, seconds = _time_one(mdp, algorithm)
                rows.append(
                    ResultRow(
                        sweep="reward_setup", label=label, algorithm=algorithm,
                        trial=trial, iterations=iterations, seconds=seconds,
                    )
                )
                print(f"setup={label:<12} {algorithm:<17} trial {trial + 1}/{TRIALS}  "
                      f"iters={iterations:>4}  {seconds:.6f}s")
    return rows


def _write_csv(rows: list[ResultRow], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "mdp_results.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["sweep", "label", "algorithm", "trial", "iterations", "seconds"])
        writer.writeheader()
        writer.writerows(rows)


def _mean(rows: list[ResultRow], key: str, algorithm: str, metric: str) -> list[tuple[str, float]]:
    groups: dict[str, list[float]] = {}
    for row in rows:
        if row["algorithm"] != algorithm:
            continue
        groups.setdefault(row[key], []).append(float(row[metric]))  # type: ignore[literal-required]
    return [(label, statistics.mean(values)) for label, values in groups.items()]


def plot_size_sweep(rows: list[ResultRow], output_dir: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping plots (the CSV still has the data).")
        return

    size_rows = [r for r in rows if r["sweep"] == "size"]
    fig, (ax_time, ax_iters) = plt.subplots(1, 2, figsize=(11, 5))

    for algorithm in ("value_iteration", "policy_iteration"):
        by_size_time = sorted(_mean(size_rows, "label", algorithm, "seconds"), key=lambda t: int(t[0]))
        sizes = [int(s) for s, _ in by_size_time]
        times = [t for _, t in by_size_time]
        ax_time.plot(sizes, times, marker="o", label=algorithm)

        by_size_iters = sorted(_mean(size_rows, "label", algorithm, "iterations"), key=lambda t: int(t[0]))
        iters = [i for _, i in by_size_iters]
        ax_iters.plot(sizes, iters, marker="o", label=algorithm)

    ax_time.set_xlabel("grid size (n, for an n x n grid)")
    ax_time.set_ylabel("mean runtime (seconds)")
    ax_time.set_title("Runtime vs. grid size")
    ax_time.set_yscale("log")
    ax_time.legend()
    ax_time.grid(True, which="both", linestyle=":", linewidth=0.5)

    ax_iters.set_xlabel("grid size (n, for an n x n grid)")
    ax_iters.set_ylabel("mean outer-loop iterations")
    ax_iters.set_title("Iteration count vs. grid size")
    ax_iters.legend()
    ax_iters.grid(True, which="both", linestyle=":", linewidth=0.5)

    fig.tight_layout()
    fig.savefig(output_dir / "size_sweep.png", dpi=150)
    print(f"Wrote {output_dir / 'size_sweep.png'}")


def main() -> None:
    output_dir = Path(__file__).resolve().parents[2] / "benchmark_data"
    rows = run_size_sweep(output_dir) + run_reward_setup_sweep(output_dir)
    _write_csv(rows, output_dir)
    plot_size_sweep(rows, output_dir)


if __name__ == "__main__":
    main()
