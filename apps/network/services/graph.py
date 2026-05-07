import heapq
from dataclasses import dataclass
from math import inf
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class EdgeWeight:
    to: str
    latency: float


class NoPathError(Exception):
    """Raised when there is no path between source and destination."""


def dijkstra_shortest_path(
    adjacency: Dict[str, Iterable[EdgeWeight]],
    source: str,
    destination: str,
) -> Optional[Tuple[float, List[str]]]:
    """
    Return (total_latency, path) for the shortest path.

    If multiple shortest paths exist, the lexicographically smallest `path`
    (tuple of node names) wins to keep results deterministic.
    """
    if source == destination:
        return 0.0, [source]

    pq: List[Tuple[float, Tuple[str, ...], str]] = []
    heapq.heappush(pq, (0.0, (source,), source))

    best_dist: Dict[str, float] = {source: 0.0}
    best_path: Dict[str, Tuple[str, ...]] = {source: (source,)}

    while pq:
        dist, path, node = heapq.heappop(pq)

        # Skip stale queue entries.
        if dist != best_dist.get(node, inf):
            continue

        if node == destination:
            return dist, list(path)

        neighbors = adjacency.get(node, [])
        # Sort for deterministic exploration order (tie-break is still by path).
        neighbors_sorted = sorted(neighbors, key=lambda e: e.to)
        for edge in neighbors_sorted:
            nxt = edge.to
            new_dist = dist + edge.latency
            new_path = path + (nxt,)

            current_best_dist = best_dist.get(nxt, inf)
            current_best_path = best_path.get(nxt, tuple())

            if new_dist < current_best_dist:
                best_dist[nxt] = new_dist
                best_path[nxt] = new_path
                heapq.heappush(pq, (new_dist, new_path, nxt))
            elif new_dist == current_best_dist and new_path < current_best_path:
                best_path[nxt] = new_path
                heapq.heappush(pq, (new_dist, new_path, nxt))

    return None


def adjacency_from_edges(
    edges: Iterable[Tuple[str, str, float]],
) -> Dict[str, List[EdgeWeight]]:
    """Helper to build adjacency from (source, destination, latency)."""
    adjacency: Dict[str, List[EdgeWeight]] = {}
    for src, dst, latency in edges:
        adjacency.setdefault(src, []).append(EdgeWeight(to=dst, latency=float(latency)))
    return adjacency

