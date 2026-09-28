"""Worked examples of applying ``dijkstra``. Run with::

    PYTHONPATH=src python -m graph_search.examples

Three applications: shortest routes on a city road network, the sample matrix
from Project Euler problem 81, and a small maze. To also solve problems 81 and
83 on a real Project Euler matrix file, pass its path::

    PYTHONPATH=src python -m graph_search.examples path/to/0081_matrix.txt
"""

from __future__ import annotations

import sys
from pathlib import Path

from graph_search.cities import build_city_graph
from graph_search.dijkstra import dijkstra, path_cost
from graph_search.grid_problems import (
    FOUR_DIRECTIONS,
    min_path_sum,
    parse_matrix,
    solve_maze,
)

# The 5x5 example from the Project Euler problem 81 statement; its minimal
# right-and-down path sum is 2427.
EULER_81_SAMPLE = [
    [131, 673, 234, 103, 18],
    [201, 96, 342, 965, 150],
    [630, 803, 746, 422, 111],
    [537, 699, 497, 121, 956],
    [805, 732, 524, 37, 331],
]

MAZE = """\
#########
#S..#...#
#.#.#.#.#
#.#...#E#
#########"""


def main(matrix_file: str | None = None) -> None:
    """Print the results of each example.

    Args:
        matrix_file: optional path to a comma-separated matrix file (the Project
            Euler format); if given, problems 81 and 83 are also solved on it.
    """
    cities = build_city_graph()
    for start, end in [("Boston", "Washington"), ("Albany", "Baltimore")]:
        path = dijkstra(cities, start, end)
        assert path is not None
        print(f"{start} -> {end}: {' -> '.join(path)} ({path_cost(cities, path):.0f} mi)")

    total, _ = min_path_sum(EULER_81_SAMPLE)
    print(f"Project Euler 81 sample: minimal path sum = {total}")

    route = solve_maze(MAZE)
    print(f"Maze: {'no route' if route is None else f'{len(route) - 1} steps'}")

    if matrix_file is not None:
        matrix = parse_matrix(Path(matrix_file).read_text())
        print(f"Project Euler 81 on {matrix_file}: {min_path_sum(matrix)[0]}")
        print(f"Project Euler 83 on {matrix_file}: {min_path_sum(matrix, FOUR_DIRECTIONS)[0]}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
