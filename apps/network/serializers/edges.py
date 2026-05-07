from rest_framework import serializers

from apps.network.models import Edge, Node


class EdgeListItemSerializer(serializers.ModelSerializer):
    source = serializers.CharField(source="source.name")
    destination = serializers.CharField(source="destination.name")

    class Meta:
        model = Edge
        fields = ["id", "source", "destination", "latency"]


class EdgeCreateSerializer(serializers.Serializer):
    source = serializers.CharField(required=False, allow_blank=False)
    destination = serializers.CharField(required=False, allow_blank=False)
    latency = serializers.FloatField(required=False)

    def validate(self, attrs):
        source_name = attrs.get("source")
        destination_name = attrs.get("destination")
        latency = attrs.get("latency")

        if not source_name or not destination_name:
            raise serializers.ValidationError("Source/destination missing")
        if latency is None or latency <= 0:
            raise serializers.ValidationError("Latency must be > 0")

        source = Node.objects.filter(name=source_name).first()
        destination = Node.objects.filter(name=destination_name).first()
        if not source or not destination:
            raise serializers.ValidationError("Nodes not found")
        if Edge.objects.filter(source=source, destination=destination).exists():
            raise serializers.ValidationError("Duplicate edge")

        attrs["source_node"] = source
        attrs["destination_node"] = destination
        return attrs
