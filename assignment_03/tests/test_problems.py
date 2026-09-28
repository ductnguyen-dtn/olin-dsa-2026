"""Tests for the problems solved with Dijkstra: Project Euler 81/83, the maze
solver, and the city road network."""

from __future__ import annotations

from pathlib import Path

import pytest

from graph_search import FOUR_DIRECTIONS, dijkstra, min_path_sum, parse_matrix, path_cost, solve_maze
from graph_search.cities import build_city_graph
from graph_search.examples import EULER_81_SAMPLE, MAZE, main


# --------------------------------------------------------------------------- #
# Project Euler 81 / 83
# --------------------------------------------------------------------------- #

def test_euler_81_sample_matches_the_problem_statement() -> None:
    total, path = min_path_sum(EULER_81_SAMPLE)
    assert total == 2427
    assert path[0] == (0, 0) and path[-1] == (4, 4)


def test_euler_81_path_only_moves_right_and_down() -> None:
    _, path = min_path_sum(EULER_81_SAMPLE)
    for (r1, c1), (r2, c2) in zip(path, path[1:]):
        assert (r2 - r1, c2 - c1) in ((0, 1), (1, 0))


def test_euler_81_path_sums_to_the_reported_total() -> None:
    total, path = min_path_sum(EULER_81_SAMPLE)
    assert sum(EULER_81_SAMPLE[r][c] for r, c in path) == total


def test_euler_83_sample_allows_four_directions() -> None:
    # The Project Euler 83 statement gives 2297 for this same matrix.
    total, _ = min_path_sum(EULER_81_SAMPLE, moves=FOUR_DIRECTIONS)
    assert total == 2297


def test_one_by_one_matrix() -> None:
    assert min_path_sum([[7]]) == (7, [(0, 0)])


def test_single_row_and_single_column() -> None:
    assert min_path_sum([[1, 2, 3]])[0] == 6
    assert min_path_sum([[1], [2], [3]])[0] == 6


def test_small_matrix_chooses_the_cheaper_side() -> None:
    #  1 9        going right first costs 1+9+1 = 11, down first costs 1+2+1 = 4
    #  2 1
    assert min_path_sum([[1, 9], [2, 1]])[0] == 4


@pytest.mark.parametrize("bad", [[], [[]], [[1, 2], [3]]])
def test_invalid_matrix_is_rejected(bad: list[list[int]]) -> None:
    with pytest.raises(ValueError):
        min_path_sum(bad)


def test_parse_matrix() -> None:
    assert parse_matrix("1,2,3\n4,5,6\n") == [[1, 2, 3], [4, 5, 6]]
    assert parse_matrix("\n7,8\n\n9,10\n") == [[7, 8], [9, 10]]


# --------------------------------------------------------------------------- #
# Maze solver
# --------------------------------------------------------------------------- #

def _steps(route: list[tuple[int, int]]) -> int:
    return len(route) - 1


def test_maze_finds_a_shortest_route() -> None:
    route = solve_maze(MAZE)
    assert route is not None
    assert _steps(route) == 12
    assert MAZE.splitlines()[route[0][0]][route[0][1]] == "S"
    assert MAZE.splitlines()[route[-1][0]][route[-1][1]] == "E"


def test_maze_route_never_crosses_a_wall_or_jumps() -> None:
    route = solve_maze(MAZE)
    assert route is not None
    lines = MAZE.splitlines()
    for r, c in route:
        assert lines[r][c] != "#"
    for (r1, c1), (r2, c2) in zip(route, route[1:]):
        assert abs(r1 - r2) + abs(c1 - c2) == 1


def test_maze_with_no_route_returns_none() -> None:
    assert solve_maze("S#E") is None


def test_maze_start_next_to_end() -> None:
    assert solve_maze("SE") == [(0, 0), (0, 1)]


def test_maze_prefers_the_shorter_of_two_routes() -> None:
    maze = "\n".join(
        [
            "#######",
            "#S...E#",
            "#.###.#",
            "#.....#",
            "#######",
        ]
    )
    route = solve_maze(maze)
    assert route is not None
    assert _steps(route) == 4  # straight across the top row


@pytest.mark.parametrize("bad", ["...", "S..", "..E", "SS.E", "S.EE"])
def test_maze_needs_exactly_one_start_and_one_end(bad: str) -> None:
    with pytest.raises(ValueError):
        solve_maze(bad)


# --------------------------------------------------------------------------- #
# City road network
# --------------------------------------------------------------------------- #

def test_city_roads_are_two_way() -> None:
    g = build_city_graph()
    assert g.get_edges("Boston")["Hartford"] == g.get_edges("Hartford")["Boston"]


def test_boston_to_washington_route() -> None:
    g = build_city_graph()
    path = dijkstra(g, "Boston", "Washington")
    assert path == ["Boston", "New York", "Philadelphia", "Washington"]
    assert path_cost(g, path) == 452


def test_shortest_path_to_a_city_with_no_direct_road() -> None:
    g = build_city_graph()
    path = dijkstra(g, "Hartford", "Baltimore")
    assert path == ["Hartford", "New York", "Philadelphia", "Baltimore"]
    assert path_cost(g, path) == 316


def test_route_to_a_city_not_on_the_map_is_none() -> None:
    assert dijkstra(build_city_graph(), "Boston", "Atlantis") is None


def test_examples_script_runs(capsys: pytest.CaptureFixture[str]) -> None:
    main()
    output = capsys.readouterr().out
    assert "Boston -> Washington" in output
    assert "2427" in output


def test_examples_script_solves_a_matrix_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    matrix_file = tmp_path / "matrix.txt"
    matrix_file.write_text("\n".join(",".join(str(v) for v in row) for row in EULER_81_SAMPLE))
    main(str(matrix_file))
    output = capsys.readouterr().out
    assert "Project Euler 81" in output and "2427" in output
    assert "2297" in output
