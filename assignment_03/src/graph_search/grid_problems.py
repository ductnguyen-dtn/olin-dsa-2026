"""Two problems solved by turning a grid into a graph and running Dijkstra.

* ``min_path_sum``: Project Euler problems 81 and 83. Walk from the top-left to
  the bottom-right of a matrix of numbers, paying each cell's value as you
  enter it, and find the cheapest total. Problem 81 allows moving only right
  and down; problem 83 allows all four directions.
* ``solve_maze``: find a shortest route through an ASCII maze.

The same idea drives both. Each open cell becomes a vertex, and an edge joins
each cell to the neighbors you may step to. Once the grid is a graph, "cheapest
route" is exactly the shortest-path problem Dijkstra solves.
"""

from __future__ import annotations

from graph_search.dijkstra import dijkstra, path_cost
from graph_search.graph import Graph

Cell = tuple[int, int]  # (row, column)

# Allowed steps as (row change, column change).
RIGHT_AND_DOWN: tuple[Cell, ...] = ((0, 1), (1, 0))  # Project Euler 81
FOUR_DIRECTIONS: tuple[Cell, ...] = ((0, 1), (1, 0), (0, -1), (-1, 0))  # Euler 83


def min_path_sum(
    matrix: list[list[int]], moves: tuple[Cell, ...] = RIGHT_AND_DOWN
) -> tuple[int, list[Cell]]:
    """Cheapest top-left to bottom-right route through ``matrix``.

    The cost of a route is the sum of the values of every cell on it, including
    the starting cell and the final cell.

    Args:
        matrix: a non-empty rectangular grid of non-negative integers.
        moves: the steps allowed from a cell, as (row change, column change)
            pairs. Defaults to right and down (Project Euler 81); pass
            ``FOUR_DIRECTIONS`` for Project Euler 83.

    Returns:
        ``(total cost, cells along the route in order)``.

    Raises:
        ValueError: if the matrix is empty or not rectangular.
    """
    if not matrix or not matrix[0] or any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("matrix must be non-empty and rectangular")
    rows, cols = len(matrix), len(matrix[0])

    graph: Graph[Cell] = Graph()
    for r in range(rows):
        for c in range(cols):
            graph.add_vertex((r, c))  # covers a 1x1 matrix, which has no edges
            for dr, dc in moves:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    # Entering a cell costs that cell's value. Charging the
                    # cost on the edge into the cell (rather than out of the
                    # one you leave) keeps the cost model the same for every
                    # edge; the start cell's own value is added separately
                    # below since no edge enters it.
                    graph.add_edge((r, c), (nr, nc), matrix[nr][nc])

    start, goal = (0, 0), (rows - 1, cols - 1)
    path = dijkstra(graph, start, goal)
    # The start and goal are always connected under the default moves, and under
    # FOUR_DIRECTIONS; a custom set of moves that disconnects them has no answer.
    if path is None:
        raise ValueError("the bottom-right cell is unreachable with the given moves")
    return matrix[0][0] + int(path_cost(graph, path)), path


def parse_matrix(text: str) -> list[list[int]]:
    """Parse comma-separated rows of integers, one row per line (the format
    Project Euler uses for its matrix files). Blank lines are ignored."""
    return [
        [int(value) for value in line.split(",")]
        for line in text.strip().splitlines()
        if line.strip()
    ]


def solve_maze(maze: str) -> list[Cell] | None:
    """Shortest route through an ASCII maze, counting each step as cost 1.

    Maze format, one string with rows separated by newlines:

    * ``#`` is a wall
    * ``S`` is the start and ``E`` is the end (exactly one of each)
    * any other character (space or ``.``) is open floor

    You may step up, down, left or right onto any non-wall cell.

    Returns:
        The ``(row, column)`` cells from ``S`` to ``E`` inclusive, or None if
        the end cannot be reached.

    Raises:
        ValueError: unless the maze contains exactly one ``S`` and one ``E``.
    """
    lines = maze.strip("\n").splitlines()
    starts = [(r, c) for r, line in enumerate(lines) for c, ch in enumerate(line) if ch == "S"]
    ends = [(r, c) for r, line in enumerate(lines) for c, ch in enumerate(line) if ch == "E"]
    if len(starts) != 1 or len(ends) != 1:
        raise ValueError("maze must contain exactly one 'S' and one 'E'")

    def is_open(r: int, c: int) -> bool:
        """True if (r, c) is inside the maze and not a wall. Rows can have
        different lengths, so the column is checked against its own row."""
        return 0 <= r < len(lines) and 0 <= c < len(lines[r]) and lines[r][c] != "#"

    graph: Graph[Cell] = Graph()
    for r, line in enumerate(lines):
        for c in range(len(line)):
            if not is_open(r, c):
                continue
            graph.add_vertex((r, c))
            for dr, dc in FOUR_DIRECTIONS:
                if is_open(r + dr, c + dc):
                    graph.add_edge((r, c), (r + dr, c + dc), 1.0)

    return dijkstra(graph, starts[0], ends[0])
