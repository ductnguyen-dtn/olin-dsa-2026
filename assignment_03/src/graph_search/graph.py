"""A directed, weighted graph stored as an adjacency map.

Matches the assignment's Kotlin ``Graph<VertexType>`` interface, translated to
Python naming (``getVertices`` -> ``get_vertices``, and so on).

Representation: ``{vertex: {neighbor: cost}}``. Every vertex that appears in the
graph has an entry, even if it has no outgoing edges, so ``get_vertices`` is
just the key set. Looking up the edges leaving a vertex is O(1) plus the size of
the result, and adding an edge is O(1).
"""

from __future__ import annotations

import math
from typing import Generic, Hashable, TypeVar

V = TypeVar("V", bound=Hashable)


class Graph(Generic[V]):
    """A directed graph whose edges carry a non-negative cost.

    Vertices can be any hashable type. Costs must be non-negative because
    Dijkstra's algorithm (the main consumer of this class) is only correct for
    non-negative edge weights, so a bad cost is rejected here at the point
    where it enters the graph rather than silently corrupting a search later.
    """

    def __init__(self) -> None:
        """Create an empty graph."""
        # Outer key: a vertex. Inner dict: its outgoing edges, neighbor -> cost.
        self._adjacency: dict[V, dict[V, float]] = {}

    def get_vertices(self) -> set[V]:
        """Return the set of all vertices in the graph (a copy, safe to modify)."""
        return set(self._adjacency)

    def add_vertex(self, vertex: V) -> None:
        """Add ``vertex`` with no edges. Does nothing if it is already present.

        ``add_edge`` adds its endpoints automatically, so this is only needed
        for a vertex that should exist without being connected to anything.
        """
        self._adjacency.setdefault(vertex, {})

    def add_edge(self, from_vertex: V, to_vertex: V, cost: float) -> None:
        """Add a directed edge ``from_vertex -> to_vertex`` with weight ``cost``.

        Both endpoints are added to the graph if they are new. If the edge
        already exists its cost is replaced, so there is at most one edge per
        ordered pair of vertices.

        Raises:
            ValueError: if ``cost`` is negative or NaN.
        """
        if math.isnan(cost) or cost < 0:
            raise ValueError(f"edge cost must be non-negative, got {cost}")
        self.add_vertex(to_vertex)
        self._adjacency.setdefault(from_vertex, {})[to_vertex] = float(cost)

    def get_edges(self, from_vertex: V) -> dict[V, float]:
        """Return the edges leaving ``from_vertex`` as ``{neighbor: cost}``.

        Returns an empty dict for a vertex with no outgoing edges, and also for
        a vertex that is not in the graph. The result is a copy, so changing it
        does not change the graph.
        """
        return dict(self._adjacency.get(from_vertex, {}))

    def clear(self) -> None:
        """Remove every vertex and edge from the graph."""
        self._adjacency.clear()

    def __contains__(self, vertex: object) -> bool:
        """True if ``vertex`` is in the graph."""
        return vertex in self._adjacency

    def __len__(self) -> int:
        """Number of vertices in the graph."""
        return len(self._adjacency)
