"""Dijkstra's shortest-path algorithm on a ``Graph``.

Dijkstra grows a set of "finished" vertices outward from the start. It keeps,
for every vertex it has seen, the cheapest cost found so far (``dist``) and the
vertex it was reached from along that route (``prev``). It repeatedly finishes
the unfinished vertex with the smallest ``dist`` and relaxes that vertex's
outgoing edges: if going through it gives a neighbor a cheaper route, the
neighbor's ``dist`` and ``prev`` are updated.

Why finishing the smallest ``dist`` first is safe: every edge cost is
non-negative, so any other route to that vertex would have to pass through a
vertex that is at least as expensive to reach, and could not come out cheaper.
That is also why ``Graph`` refuses negative edge costs.

With a binary heap holding the frontier, the running time is
O((V + E) log V), where V is the number of vertices and E the number of edges.
"""

from __future__ import annotations

from typing import Hashable, TypeVar

from graph_search.graph import Graph
from graph_search.priority_queue import MinPriorityQueue

V = TypeVar("V", bound=Hashable)


def dijkstra(graph: Graph[V], start: V, destination: V) -> list[V] | None:
    """Find a cheapest path from ``start`` to ``destination``.

    Args:
        graph: the graph to search.
        start: the vertex the path begins at.
        destination: the vertex the path ends at.

    Returns:
        The vertices along a cheapest path, in order, including both ``start``
        and ``destination`` (so the path from a vertex to itself is
        ``[start]``). Returns None if there is no path, including when either
        vertex is not in the graph. If several paths tie for cheapest, one of
        them is returned.
    """
    if start not in graph or destination not in graph:
        return None

    # dist[v]: cheapest known cost to reach v. A vertex appears here as soon as
    # it is first reached, so "v in dist and v not in finished" means v is
    # currently in the frontier queue.
    dist: dict[V, float] = {start: 0.0}
    # prev[v]: the vertex just before v on the cheapest known route to v.
    prev: dict[V, V] = {}
    finished: set[V] = set()

    frontier: MinPriorityQueue[V] = MinPriorityQueue()
    frontier.add_with_priority(start, 0.0)

    while not frontier.is_empty():
        current = frontier.next()
        # The queue only returns None when empty, which the loop condition rules
        # out; this narrows the type for the checker.
        assert current is not None
        finished.add(current)

        # The first time the destination is taken off the queue its cost is
        # final, so there is no need to explore the rest of the graph.
        if current == destination:
            return _rebuild_path(prev, start, destination)

        for neighbor, edge_cost in graph.get_edges(current).items():
            if neighbor in finished:
                continue  # already has its final, cheapest cost
            candidate = dist[current] + edge_cost
            if neighbor not in dist or candidate < dist[neighbor]:
                # Found a first route to neighbor, or a cheaper one than before.
                dist[neighbor] = candidate
                prev[neighbor] = current
                # add_with_priority inserts a new vertex or lowers an existing
                # one's priority, which is exactly the two cases here.
                frontier.add_with_priority(neighbor, candidate)

    # The queue emptied without ever reaching the destination: no path exists.
    return None


def path_cost(graph: Graph[V], path: list[V]) -> float:
    """Total cost of following ``path`` through ``graph``.

    A path of one vertex costs 0.

    Raises:
        KeyError: if two consecutive vertices in ``path`` are not joined by an
            edge in ``graph``.
    """
    total = 0.0
    for here, there in zip(path, path[1:]):
        total += graph.get_edges(here)[there]
    return total


def _rebuild_path(prev: dict[V, V], start: V, destination: V) -> list[V]:
    """Walk ``prev`` backward from ``destination`` to ``start`` and return the
    path in start-to-destination order."""
    path = [destination]
    while path[-1] != start:
        path.append(prev[path[-1]])
    path.reverse()
    return path
