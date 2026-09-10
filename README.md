# Olin Data Structures & Algorithms 2026

Coursework for [olindsa2026](https://olindsa2026.github.io). One repo for the
whole course; each assignment is its own folder.

Language: Python with type hints (`mypy --strict`).

| Folder | Assignment | Notes |
|---|---|---|
| [`hw1/`](hw1/) | Assignment 1 — Hello World + Getting to Know You | Spot Micro servo-code port, meeting-conflict scheduler |

Each folder is self-contained: its own `pyproject.toml`, `Makefile`, and
`.venv`. From inside an assignment folder:

```bash
make venv    # one-time
make check   # pytest + mypy
```
