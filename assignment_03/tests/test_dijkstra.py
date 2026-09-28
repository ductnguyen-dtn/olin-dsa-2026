"""Tests for dijkstra and path_cost.

The randomized test checks Dijkstra against Bellman-Ford, a slower algorithm
that is simple enough to trust as an oracle: the two must agree on whether a
path exists and on its cost, for every start and destination.
"""

from __future__ import annotations

import math
import random

import pytest

from graph_search import Graph, dijkstra, path_cost


def _diamond() -> Graph[str]:
    """     b
          /   \\
        a       d      a->b->d costs 2+2, a->c->d costs 1+5, a->d costs 10
          \\   /
            c
    """
    g: Graph[str] = Graph()
    g.add_edge("a", "b", 2.0)
    g.add_edge("b", "d", 2.0)
    g.add_edge("a", "c", 1.0)
    g.add_edge("c", "d", 5.0)
    g.add_edge("a", "d", 10.0)
    return g


def test_finds_the_cheapest_path_not_the_fewest_edges() -> None:
    g = _diamond()
    # The direct edge a->d has the fewest edges but is the most expensive.
    assert dijkstra(g, "a", "d") == ["a", "b", "d"]


def test_returns_the_path_itself_not_just_the_cost() -> None:
    path = dijkstra(_diamond(), "a", "d")
    assert path is not None
    assert path[0] == "a" and path[-1] == "d"
    assert path_cost(_diamond(), path) == 4.0


def test_returns_none_when_no_path_exists() -> None:
    g = _diamond()
    g.add_vertex("island")
    assert dijkstra(g, "a", "island") is None


def test_returns_none_when_only_a_backward_edge_exists() -> None:
    g: Graph[str] = Graph()
    g.add_edge("b", "a", 1.0)  # directed: you can go b->a, not a->b
    assert dijkstra(g, "a", "b") is None
    assert dijkstra(g, "b", "a") == ["b", "a"]


def test_path_from_a_vertex_to_itself_is_just_that_vertex() -> None:
    assert dijkstra(_diamond(), "a", "a") == ["a"]


def test_unknown_start_or_destination_returns_none() -> None:
    g = _diamond()
    assert dijkstra(g, "nope", "a") is None
    assert dijkstra(g, "a", "nope") is None


def test_empty_graph_returns_none() -> None:
    g: Graph[str] = Graph()
    assert dijkstra(g, "a", "b") is None


def test_single_edge() -> None:
    g: Graph[str] = Graph()
    g.add_edge("a", "b", 3.0)
    assert dijkstra(g, "a", "b") == ["a", "b"]


def test_zero_cost_edges() -> None:
    g: Graph[str] = Graph()
    g.add_edge("a", "b", 0.0)
    g.add_edge("b", "c", 0.0)
    assert dijkstra(g, "a", "c") == ["a", "b", "c"]


def test_cheaper_route_discovered_later_replaces_an_earlier_one() -> None:
    # Reaching "m" first costs 10 via a->m, but a->x->m costs 1 + 1. Dijkstra
    # must lower m's cost when it finds the second route.
    g: Graph[str] = Graph()
    g.add_edge("a", "m", 10.0)
    g.add_edge("a", "x", 1.0)
    g.add_edge("x", "m", 1.0)
    g.add_edge("m", "z", 1.0)
    assert dijkstra(g, "a", "z") == ["a", "x", "m", "z"]


def test_cycles_do_not_cause_infinite_loops() -> None:
    g: Graph[str] = Graph()
    g.add_edge("a", "b", 1.0)
    g.add_edge("b", "a", 1.0)
    g.add_edge("b", "c", 1.0)
    g.add_edge("c", "b", 1.0)
    assert dijkstra(g, "a", "c") == ["a", "b", "c"]


def test_self_loops_are_ignored() -> None:
    g: Graph[str] = Graph()
    g.add_edge("a", "a", 1.0)
    g.add_edge("a", "b", 2.0)
    assert dijkstra(g, "a", "b") == ["a", "b"]


def test_ties_return_a_path_of_the_optimal_cost() -> None:
    g: Graph[str] = Graph()
    g.add_edge("a", "b", 1.0)
    g.add_edge("a", "c", 1.0)
    g.add_edge("b", "d", 1.0)
    g.add_edge("c", "d", 1.0)
    path = dijkstra(g, "a", "d")
    assert path in (["a", "b", "d"], ["a", "c", "d"])


def test_does_not_modify_the_graph() -> None:
    g = _diamond()
    before = {v: g.get_edges(v) for v in g.get_vertices()}
    dijkstra(g, "a", "d")
    assert {v: g.get_edges(v) for v in g.get_vertices()} == before


def test_path_cost_of_single_vertex_is_zero() -> None:
    assert path_cost(_diamond(), ["a"]) == 0.0


def test_path_cost_of_missing_edge_raises() -> None:
    with pytest.raises(KeyError):
        path_cost(_diamond(), ["d", "a"])


def _bellman_ford(graph: Graph[int], start: int) -> dict[int, float]:
    """Reference shortest costs from ``start`` to every vertex (inf if unreachable)."""
    dist = {v: math.inf for v in graph.get_vertices()}
    dist[start] = 0.0
    for _ in range(len(dist)):
        for u in list(dist):
            for v, cost in graph.get_edges(u).items():
                if dist[u] + cost < dist[v]:
                    dist[v] = dist[u] + cost
    return dist


@pytest.mark.parametrize("seed", range(40))
def test_matches_bellman_ford_on_random_graphs(seed: int) -> None:
    rng = random.Random(seed)
    n = rng.randint(1, 12)
    g: Graph[int] = Graph()
    for v in range(n):
        g.add_vertex(v)
    for _ in range(rng.randint(0, n * 3)):
        g.add_edge(rng.randrange(n), rng.randrange(n), float(rng.randint(0, 9)))

    for start in range(n):
        expected = _bellman_ford(g, start)
        for destination in range(n):
            path = dijkstra(g, start, destination)
            if math.isinf(expected[destination]):
                assert path is None
            else:
                assert path is not None
                assert path[0] == start and path[-1] == destination
                assert path_cost(g, path) == expected[destination]
