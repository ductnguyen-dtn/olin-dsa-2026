# Assignment 6 Deep Dive: Policy Iteration vs. Value Iteration

[Assignment page](https://olindsa2026.github.io/assignments/assignment_06.html)

## What this is

A from-scratch implementation and head-to-head comparison of the two
classic dynamic-programming algorithms for solving a Markov Decision
Process with a fully known model: **value iteration** and **policy
iteration**. Both solve the Bellman optimality equation on a gridworld MDP
and are checked against each other, including against a hand-worked
example small enough to verify by arithmetic.

This is the tabular ancestor of PPO, the deep-RL algorithm used to train
locomotion policies for the G1 humanoid and SpotMicro quadruped projects
(see `~/Documents/Claude/Unitree_G1/` and `~/Documents/Claude/Robot_Dog/`).
The writeup ties the two together directly.

## Structure

- `src/deep_dive/gridworld.py`: the MDP itself, a stochastic "slippery
  floor" gridworld (states, actions, a transition model with noise, and
  rewards), in the style of the classic Russell & Norvig / Sutton & Barto
  gridworld.
- `src/deep_dive/dp.py`: `value_iteration` and `policy_iteration`, plus the
  shared `q_value` / `extract_policy` helpers both are built from.
- `src/deep_dive/benchmark.py`: real benchmark run, sweeping grid size and
  reward/noise setup, timing both algorithms and counting outer-loop
  iterations. Writes `benchmark_data/mdp_results.csv` and a plot.
- `tests/test_gridworld.py`, `tests/test_dp.py`: correctness tests,
  including a hand-verified 1x3 corridor (`test_hand_verified_corridor`)
  and a cross-check that both algorithms converge to the same value
  function and, up to genuine ties, the same policy across several
  gridworlds.
- `docs/policy_vs_value_iteration.md`: the writeup. Covers the Bellman
  equation, why policy iteration converges, the real benchmark results,
  and the connection back to PPO.

## Running the checks

```bash
make venv    # one-time
make check   # pytest + mypy
```

## Running the benchmark

```bash
PYTHONPATH=src python -m deep_dive.benchmark
```

## AI assistance

The code, its docstrings and inline comments, and the writeup in `docs/`
were produced with the help of Claude (Anthropic), under my direction and
review, following the project proposal and self-assessment rubric I wrote
for this assignment.
