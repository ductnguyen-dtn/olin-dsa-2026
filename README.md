# Olin Data Structures & Algorithms 2026

Coursework for [olindsa2026](https://olindsa2026.github.io). One repo for the
whole course; each assignment is its own folder.

Language: Python with type hints (`mypy --strict`).

| Folder | Assignment | Notes |
|---|---|---|
| [`assignment_01/`](assignment_01/) | Assignment 1: Hello World + Getting to Know You | Spot Micro servo-code port, meeting-conflict scheduler |
| [`assignment_02/`](assignment_02/) | Assignment 2: Linked Data Structures | Doubly linked list, Stack and Queue built on it, stack-reversal practice problem |

Each folder is self-contained: its own `pyproject.toml`, `Makefile`, and
`.venv`. From inside an assignment folder:

```bash
make venv    # one-time
make check   # pytest + mypy
```
