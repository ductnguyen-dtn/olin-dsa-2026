"""Tests for Graph."""

from __future__ import annotations

import math

import pytest

from graph_search import Graph


def test_new_graph_is_empty() -> None:
    g: Graph[str] = Graph()
    assert g.get_vertices() == set()
    assert len(g) == 0


def test_add_edge_adds_both_endpoints() -> None:
    g: Graph[str] = Graph()
    g.add_edge("a", "b", 2.5)
    assert g.get_vertices() == {"a", "b"}


def test_edges_are_directed() -> None:
    g: Graph[str] = Graph()
    g.add_edge("a", "b", 1.0)
    assert g.get_edges("a") == {"b": 1.0}
    assert g.get_edges("b") == {}


def test_get_edges_returns_all_neighbors_with_costs() -> None:
    g: Graph[int] = Graph()
    g.add_edge(1, 2, 1.0)
    g.add_edge(1, 3, 2.0)
    g.add_edge(2, 3, 5.0)
    assert g.get_edges(1) == {2: 1.0, 3: 2.0}
    assert g.get_edges(2) == {3: 5.0}


def test_get_edges_of_unknown_vertex_is_empty() -> None:
    g: Graph[str] = Graph()
    assert g.get_edges("nope") == {}


def test_adding_an_existing_edge_replaces_its_cost() -> None:
    g: Graph[str] = Graph()
    g.add_edge("a", "b", 1.0)
    g.add_edge("a", "b", 9.0)
    assert g.get_edges("a") == {"b": 9.0}


def test_add_vertex_creates_an_isolated_vertex() -> None:
    g: Graph[str] = Graph()
    g.add_vertex("lonely")
    assert g.get_vertices() == {"lonely"}
    assert g.get_edges("lonely") == {}


def test_add_vertex_keeps_existing_edges() -> None:
    g: Graph[str] = Graph()
    g.add_edge("a", "b", 1.0)
    g.add_vertex("a")
    assert g.get_edges("a") == {"b": 1.0}


def test_self_loop_is_allowed() -> None:
    g: Graph[str] = Graph()
    g.add_edge("a", "a", 3.0)
    assert g.get_edges("a") == {"a": 3.0}
    assert g.get_vertices() == {"a"}


def test_zero_cost_edge_is_allowed() -> None:
    g: Graph[str] = Graph()
    g.add_edge("a", "b", 0.0)
    assert g.get_edges("a") == {"b": 0.0}


@pytest.mark.parametrize("bad_cost", [-1.0, -0.001, math.nan])
def test_negative_or_nan_cost_is_rejected(bad_cost: float) -> None:
    g: Graph[str] = Graph()
    with pytest.raises(ValueError):
        g.add_edge("a", "b", bad_cost)
    assert len(g) == 0  # a rejected edge must not leave its endpoints behind


def test_clear_removes_everything() -> None:
    g: Graph[str] = Graph()
    g.add_edge("a", "b", 1.0)
    g.add_edge("b", "c", 1.0)
    g.clear()
    assert g.get_vertices() == set()
    assert g.get_edges("a") == {}
    g.add_edge("x", "y", 1.0)  # still usable afterwards
    assert g.get_vertices() == {"x", "y"}


def test_get_vertices_returns_a_copy() -> None:
    g: Graph[str] = Graph()
    g.add_edge("a", "b", 1.0)
    g.get_vertices().add("intruder")
    assert g.get_vertices() == {"a", "b"}


def test_get_edges_returns_a_copy() -> None:
    g: Graph[str] = Graph()
    g.add_edge("a", "b", 1.0)
    g.get_edges("a")["c"] = 5.0
    assert g.get_edges("a") == {"b": 1.0}


def test_contains() -> None:
    g: Graph[str] = Graph()
    g.add_edge("a", "b", 1.0)
    assert "a" in g
    assert "b" in g
    assert "c" not in g


def test_works_with_tuple_vertices() -> None:
    g: Graph[tuple[int, int]] = Graph()
    g.add_edge((0, 0), (0, 1), 1.0)
    assert g.get_edges((0, 0)) == {(0, 1): 1.0}
