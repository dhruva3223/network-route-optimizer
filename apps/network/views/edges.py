import json

from django.http import HttpRequest, HttpResponse, JsonResponse
from rest_framework.views import APIView as DRFAPIView

from apps.network.models import Edge, Node


class EdgeListCreateView(DRFAPIView):
    def _read_json(self, request: HttpRequest) -> dict:
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    def get(self, request: HttpRequest) -> HttpResponse:
        edges = Edge.objects.select_related("source", "destination").order_by(
            "id"
        )
        return JsonResponse(
            {
                "edges": [
                    {
                        "id": e.id,
                        "source": e.source.name,
                        "destination": e.destination.name,
                        "latency": e.latency,
                    }
                    for e in edges
                ]
            }
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        payload = self._read_json(request)
        source_name = payload.get("source")
        destination_name = payload.get("destination")
        latency = payload.get("latency")

        if not source_name or not destination_name:
            return JsonResponse({"error": "Source/destination missing"}, status=400)

        try:
            latency_value = float(latency)
        except (TypeError, ValueError):
            return JsonResponse({"error": "Latency must be > 0"}, status=400)

        if latency_value <= 0:
            return JsonResponse({"error": "Latency must be > 0"}, status=400)

        source = Node.objects.filter(name=source_name).first()
        destination = Node.objects.filter(name=destination_name).first()
        if not source or not destination:
            return JsonResponse({"error": "Nodes not found"}, status=400)

        if Edge.objects.filter(source=source, destination=destination).exists():
            return JsonResponse({"error": "Duplicate edge"}, status=400)

        edge = Edge.objects.create(
            source=source, destination=destination, latency=latency_value
        )
        return JsonResponse(
            {
                "id": edge.id,
                "source": edge.source.name,
                "destination": edge.destination.name,
                "latency": edge.latency,
            },
            status=201,
        )


class EdgeDetailView(DRFAPIView):
    def delete(self, request: HttpRequest, pk: int) -> HttpResponse:
        try:
            edge = Edge.objects.get(pk=pk)
        except Edge.DoesNotExist:
            return JsonResponse({"error": "Edge not found"}, status=404)

        edge.delete()
        return JsonResponse({}, status=204, safe=False)

