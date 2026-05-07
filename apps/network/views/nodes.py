from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.network.models import Node
from apps.network.serializers import NodeCreateSerializer, NodeListItemSerializer


class NodeListCreateView(APIView):
    def get(self, request):
        nodes = Node.objects.all().order_by("id")
        return Response(
            {"nodes": NodeListItemSerializer(nodes, many=True).data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = NodeCreateSerializer(data=request.data or {})
        if not serializer.is_valid():
            return Response(
                {"error": "Name missing or duplicate"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        node = Node.objects.create(name=serializer.validated_data["name"])
        return Response(
            NodeListItemSerializer(node).data,
            status=status.HTTP_201_CREATED,
        )


class NodeDetailView(APIView):
    def delete(self, request, pk: int):
        node = Node.objects.filter(pk=pk).first()
        if not node:
            return Response({"error": "Node not found"}, status=status.HTTP_404_NOT_FOUND)
        node.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

