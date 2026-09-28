"""A small road network between Northeast US cities, for shortest-path examples.

Distances are approximate driving miles between neighboring cities, rounded, and
are meant as realistic sample data rather than a navigation reference. Roads are
two-way, so each one is added as a pair of directed edges.
"""

from __future__ import annotations

from graph_search.graph import Graph

# (city, city, approximate driving miles)
ROADS: tuple[tuple[str, str, float], ...] = (
    ("Boston", "Hartford", 102),
    ("Boston", "Albany", 170),
    ("Boston", "New York", 215),
    ("Hartford", "New York", 118),
    ("Hartford", "Albany", 100),
    ("Albany", "New York", 150),
    ("Albany", "Pittsburgh", 400),
    ("New York", "Philadelphia", 97),
    ("Philadelphia", "Baltimore", 101),
    ("Philadelphia", "Washington", 140),
    ("Philadelphia", "Pittsburgh", 305),
    ("Baltimore", "Washington", 40),
    ("Baltimore", "Pittsburgh", 250),
    ("Washington", "Pittsburgh", 240),
)


def build_city_graph() -> Graph[str]:
    """Build the road network as a graph with two directed edges per road."""
    graph: Graph[str] = Graph()
    for a, b, miles in ROADS:
        graph.add_edge(a, b, miles)
        graph.add_edge(b, a, miles)
    return graph
