# Olin DSA 2026 — Assignment 1

Language choice: **Python** with type hints (`mypy --strict`), permitted under
the assignment's "statically typed or has static-typing tooling" rule.

## Contents

| Path | Component |
|---|---|
| [`src/spotmicro_servo/`](src/spotmicro_servo/) | Spot Micro servo-movement code ported from C++ to typed Python |
| [`src/meeting_scheduler/`](src/meeting_scheduler/) | Meeting-conflict detection — naive and sorted |
| [`tests/`](tests/) | pytest suite for both (107 tests) |
| [`docs/porting.md`](docs/porting.md) | Port: purpose of the original code and how it was translated |
| [`docs/meeting_scheduler_analysis.md`](docs/meeting_scheduler_analysis.md) | Meeting scheduler runtime analysis |

## Running the checks

```bash
make venv     # one-time: create .venv, install pytest + mypy
make check    # pytest + mypy
```

> This machine sources ROS 2 Jazzy in `.bashrc`, which puts `/opt/ros` on
> `PYTHONPATH` and breaks bare `pytest`. The `Makefile` runs everything in a
> clean environment; to run tools by hand use
> `env -u PYTHONPATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest`.

## spotmicro_servo

Reproduces the servo-command math from the Spot Micro C++ node
`spot_micro_motion_cmd` and the `i2cpwm_board` driver: joint angle (rad) +
per-servo calibration → proportional command in `[-1, 1]` → raw 12-bit PWM
count in `[0, 4096]`. No ROS, no hardware. See [`docs/porting.md`](docs/porting.md).

## meeting_scheduler

`Meeting(start, end, label)` is a half-open interval; meetings that touch at an
endpoint do not conflict. `has_conflict_*` answer yes/no; `find_all_conflicts_*`
list the pairs. `_naive` is O(n²) all-pairs; `_sorted` sorts first and is
O(n log n) for the existence check, O(n log n + k) to list k pairs. Full
analysis in [`docs/meeting_scheduler_analysis.md`](docs/meeting_scheduler_analysis.md).
