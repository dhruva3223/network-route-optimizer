from typing import Optional, Tuple

from apps.network.models import Edge, Node, RouteQuery
from apps.network.services.graph import adjacency_from_edges, dijkstra_shortest_path


def find_shortest_route(
    source_name: str, destination_name: str
) -> Optional[Tuple[float, list[str]]]:
    edges = Edge.objects.select_related("source", "destination").all()
    adjacency = adjacency_from_edges(
        (e.source.name, e.destination.name, e.latency) for e in edges
    )
    return dijkstra_shortest_path(adjacency, source_name, destination_name)


def persist_route_query(
    source: Node, destination: Node, total_latency: float, path: list[str]
) -> RouteQuery:
    return RouteQuery.objects.create(
        source=source,
        destination=destination,
        total_latency=total_latency,
        path=path,
    )
