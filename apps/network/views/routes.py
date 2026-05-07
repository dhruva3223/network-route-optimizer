from datetime import datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.network.models import Edge, Node, RouteQuery
from apps.network.services.graph import adjacency_from_edges, dijkstra_shortest_path


class ShortestRouteView(APIView):
    def post(self, request):
        payload = request.data or {}
        source_name = payload.get("source")
        destination_name = payload.get("destination")

        if not source_name or not destination_name:
            return Response(
                {"error": "Invalid or non-existent nodes"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        source = Node.objects.filter(name=source_name).first()
        destination = Node.objects.filter(name=destination_name).first()
        if not source or not destination:
            return Response(
                {"error": "Invalid or non-existent nodes"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        edges = Edge.objects.select_related("source", "destination").all()
        adjacency = adjacency_from_edges(
            (e.source.name, e.destination.name, e.latency) for e in edges
        )
        result = dijkstra_shortest_path(adjacency, source_name, destination_name)
        if result is None:
            return Response(
                {
                    "error": f"No path exists between {source_name} and {destination_name}"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        total_latency, path = result
        route = RouteQuery.objects.create(
            source=source,
            destination=destination,
            total_latency=total_latency,
            path=path,
        )

        return Response(
            {"total_latency": route.total_latency, "path": route.path},
            status=status.HTTP_200_OK,
        )


class RouteHistoryView(APIView):
    def get(self, request):
        qs = RouteQuery.objects.select_related("source", "destination").all()

        source = request.query_params.get("source")
        destination = request.query_params.get("destination")
        if source:
            qs = qs.filter(source__name=source)
        if destination:
            qs = qs.filter(destination__name=destination)

        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        if date_from:
            qs = qs.filter(created_at__gte=_parse_dt(date_from))
        if date_to:
            qs = qs.filter(created_at__lte=_parse_dt(date_to))

        limit = request.query_params.get("limit")
        if limit:
            try:
                limit_value = int(limit)
                if limit_value > 0:
                    qs = qs[:limit_value]
            except ValueError:
                pass

        data = [
            {
                "id": r.id,
                "source": r.source.name,
                "destination": r.destination.name,
                "total_latency": r.total_latency,
                "path": r.path,
                "created_at": r.created_at.isoformat().replace("+00:00", "Z"),
            }
            for r in qs
        ]
        return Response(data, status=status.HTTP_200_OK)


def _parse_dt(value: str) -> datetime:
    # Accept both "...Z" and "+00:00" forms.
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    # Query params commonly decode `+` to space unless percent-encoded.
    value = value.replace(" ", "+")
    return datetime.fromisoformat(value)

