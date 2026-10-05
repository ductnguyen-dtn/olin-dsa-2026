# Olin Data Structures & Algorithms 2026

Coursework for [olindsa2026](https://olindsa2026.github.io). One repo for the
whole course; each assignment is its own folder.

Language: Python with type hints (`mypy --strict`).

| Folder | Assignment | Notes |
|---|---|---|
| [`assignment_01/`](assignment_01/) | Assignment 1: Hello World + Getting to Know You | Spot Micro servo-code port, meeting-conflict scheduler |
| [`assignment_02/`](assignment_02/) | Assignment 2: Linked Data Structures | Doubly linked list, Stack and Queue built on it, stack-reversal practice problem |
| [`assignment_03/`](assignment_03/) | Assignment 3: Graph Searching and Shortest Paths | Weighted digraph, min priority queue on a hand-written heap, Dijkstra, Euler 81/83 and maze solver |
| [`assignment_04/`](assignment_04/) | Assignment 4: Sorting Algorithms | Insertion/merge/quick/heap sort, real benchmark data + plot, AlphaDev writeup, master theorem worksheet |

Each folder is self-contained: its own `pyproject.toml`, `Makefile`, and
`.venv`. From inside an assignment folder:

```bash
make venv    # one-time
make check   # pytest + mypy
```
