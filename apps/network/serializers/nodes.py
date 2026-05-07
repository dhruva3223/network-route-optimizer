from rest_framework import serializers

from apps.network.models import Node


class NodeListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ["id", "name"]


class NodeCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=False, max_length=255)

    def validate(self, attrs):
        name = attrs.get("name")
        if not name or Node.objects.filter(name=name).exists():
            raise serializers.ValidationError("Name missing or duplicate")
        return attrs
