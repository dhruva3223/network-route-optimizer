from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.network.models import Edge
from apps.network.serializers import EdgeCreateSerializer, EdgeListItemSerializer


class EdgeListCreateView(APIView):
    def get(self, request):
        edges = Edge.objects.select_related("source", "destination").order_by("id")
        return Response(
            {"edges": EdgeListItemSerializer(edges, many=True).data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = EdgeCreateSerializer(data=request.data or {})
        if not serializer.is_valid():
            message = serializer.errors.get("non_field_errors", ["Invalid data"])[0]
            return Response({"error": str(message)}, status=status.HTTP_400_BAD_REQUEST)

        edge = Edge.objects.create(
            source=serializer.validated_data["source_node"],
            destination=serializer.validated_data["destination_node"],
            latency=serializer.validated_data["latency"],
        )
        return Response(EdgeListItemSerializer(edge).data, status=status.HTTP_201_CREATED)


class EdgeDetailView(APIView):
    def delete(self, request, pk: int):
        edge = Edge.objects.filter(pk=pk).first()
        if not edge:
            return Response({"error": "Edge not found"}, status=status.HTTP_404_NOT_FOUND)
        edge.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

