# Olin DSA 2026: Assignment 3, Graph Searching and Shortest Paths

Language: Python with type hints (`mypy --strict`). Python has no KDoc; every
class and function has a docstring in its place, plus inline comments on the
non-obvious steps of the heap and of Dijkstra's algorithm.

## Contents

| Path | Component |
|---|---|
| [`src/graph_search/graph.py`](src/graph_search/graph.py) | `Graph`: directed, weighted graph (`get_vertices`, `add_edge`, `get_edges`, `clear`) |
| [`src/graph_search/min_heap.py`](src/graph_search/min_heap.py) | `MinHeap`: binary min heap written from scratch, with O(log n) priority updates |
| [`src/graph_search/priority_queue.py`](src/graph_search/priority_queue.py) | `MinPriorityQueue`: thin wrapper over the heap (`is_empty`, `add_with_priority`, `next`, `adjust_priority`) |
| [`src/graph_search/dijkstra.py`](src/graph_search/dijkstra.py) | `dijkstra(graph, start, destination)`: returns the shortest path as a list of vertices, or `None` |
| [`src/graph_search/grid_problems.py`](src/graph_search/grid_problems.py) | Project Euler 81 and 83 (`min_path_sum`) and a maze solver (`solve_maze`), both built on Dijkstra |
| [`src/graph_search/cities.py`](src/graph_search/cities.py) | A city road network for shortest-path examples |
| [`src/graph_search/examples.py`](src/graph_search/examples.py) | Runnable examples of applying Dijkstra |
| [`tests/`](tests/) | pytest suite (227 tests) |

## Running

```bash
make venv     # one-time: create .venv, install pytest + mypy
make check    # pytest + mypy

PYTHONPATH=src .venv/bin/python -m graph_search.examples
```

> This machine sources ROS 2 Jazzy in `.bashrc`, which puts `/opt/ros` on
> `PYTHONPATH` and breaks bare `pytest`. The Makefile runs everything in a
> clean environment.

## Design notes

**Own heap.** The priority queue sits on a heap written from scratch rather than
Python's `heapq`. `heapq` has no way to change an item's priority, so the heap
keeps a second dict from item to its position in the array, which makes
`adjust_priority` O(log n) instead of a linear search.

**Unique elements.** The priority queue holds each element at most once, so
"the element" in `adjust_priority` is unambiguous. Adding an element that is
already present updates its priority instead of adding a copy.

**Non-negative costs.** `Graph.add_edge` rejects negative and NaN costs.
Dijkstra's algorithm is only correct for non-negative weights, so the check is
done where a bad cost enters the graph instead of failing later in a search.

**Applications.** `min_path_sum` turns a matrix into a graph (one vertex per
cell, an edge into each cell it may move to, costing that cell's value) and
runs Dijkstra. On the real 80x80 Project Euler matrix it gives 427337 for
problem 81 and 425185 for problem 83. `solve_maze` does the same for ASCII
mazes with unit-cost steps.

**Running time.** Dijkstra with a binary heap is O((V + E) log V).
