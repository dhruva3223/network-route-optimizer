import json

from django.http import HttpRequest, HttpResponse, JsonResponse
from rest_framework.views import APIView as DRFAPIView
from apps.network.models import Node


class NodeListCreateView(DRFAPIView):
    def _read_json(self, request: HttpRequest) -> dict:
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
            return payload if isinstance(payload, dict) else {}
        except Exception:
            return {}

    def get(self, request: HttpRequest) -> HttpResponse:
        nodes = Node.objects.all().order_by("id")
        return JsonResponse({"nodes": [{"id": n.id, "name": n.name} for n in nodes]})

    def post(self, request: HttpRequest) -> HttpResponse:
        payload = self._read_json(request)
        name = payload.get("name")
        if not name:
            return JsonResponse({"error": "Name missing or duplicate"}, status=400)

        if Node.objects.filter(name=name).exists():
            return JsonResponse({"error": "Name missing or duplicate"}, status=400)

        node = Node.objects.create(name=name)
        return JsonResponse({"id": node.id, "name": node.name}, status=201)


class NodeDetailView(DRFAPIView):
    def delete(self, request: HttpRequest, pk: int) -> HttpResponse:
        try:
            node = Node.objects.get(pk=pk)
        except Node.DoesNotExist:
            return JsonResponse({"error": "Node not found"}, status=404)

        node.delete()
        return JsonResponse({}, status=204, safe=False)

