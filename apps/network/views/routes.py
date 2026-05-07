from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.network.models import RouteQuery
from apps.network.serializers import (
    RouteHistoryItemSerializer,
    RouteHistoryQuerySerializer,
    ShortestRouteRequestSerializer,
)
from apps.network.services.route_service import find_shortest_route, persist_route_query


class ShortestRouteView(APIView):
    def post(self, request):
        serializer = ShortestRouteRequestSerializer(data=request.data or {})
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid or non-existent nodes"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        source_name = serializer.validated_data["source"]
        destination_name = serializer.validated_data["destination"]
        result = find_shortest_route(source_name, destination_name)
        if result is None:
            return Response(
                {"error": f"No path exists between {source_name} and {destination_name}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        total_latency, path = result
        route = persist_route_query(
            source=serializer.validated_data["source_node"],
            destination=serializer.validated_data["destination_node"],
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
        query_serializer = RouteHistoryQuerySerializer(data=request.query_params)
        if not query_serializer.is_valid():
            return Response(
                {"error": query_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        params = query_serializer.validated_data

        source = params.get("source")
        destination = params.get("destination")
        if source:
            qs = qs.filter(source__name=source)
        if destination:
            qs = qs.filter(destination__name=destination)

        date_from = params.get("date_from")
        date_to = params.get("date_to")
        if date_from:
            qs = qs.filter(created_at__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__lte=date_to)

        limit = params.get("limit")
        if limit:
            qs = qs[:limit]

        return Response(
            RouteHistoryItemSerializer(qs, many=True).data,
            status=status.HTTP_200_OK,
        )
