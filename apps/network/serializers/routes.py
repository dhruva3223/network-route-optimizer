from datetime import datetime, timezone as dt_timezone

from rest_framework import serializers

from apps.network.models import Node, RouteQuery


class ShortestRouteRequestSerializer(serializers.Serializer):
    source = serializers.CharField(required=False, allow_blank=False)
    destination = serializers.CharField(required=False, allow_blank=False)

    def validate(self, attrs):
        source_name = attrs.get("source")
        destination_name = attrs.get("destination")
        if not source_name or not destination_name:
            raise serializers.ValidationError("Invalid or non-existent nodes")

        source = Node.objects.filter(name=source_name).first()
        destination = Node.objects.filter(name=destination_name).first()
        if not source or not destination:
            raise serializers.ValidationError("Invalid or non-existent nodes")

        attrs["source_node"] = source
        attrs["destination_node"] = destination
        return attrs


class RouteHistoryQuerySerializer(serializers.Serializer):
    source = serializers.CharField(required=False)
    destination = serializers.CharField(required=False)
    limit = serializers.IntegerField(required=False, min_value=1)
    date_from = serializers.CharField(required=False)
    date_to = serializers.CharField(required=False)

    def validate_date_from(self, value: str):
        try:
            return _parse_dt(value)
        except ValueError as exc:
            raise serializers.ValidationError("Invalid datetime format") from exc

    def validate_date_to(self, value: str):
        try:
            return _parse_dt(value)
        except ValueError as exc:
            raise serializers.ValidationError("Invalid datetime format") from exc


class RouteHistoryItemSerializer(serializers.ModelSerializer):
    source = serializers.CharField(source="source.name")
    destination = serializers.CharField(source="destination.name")
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = RouteQuery
        fields = [
            "id",
            "source",
            "destination",
            "total_latency",
            "path",
            "created_at",
        ]

    def get_created_at(self, obj: RouteQuery) -> str:
        return (
            obj.created_at.astimezone(dt_timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )


def _parse_dt(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    value = value.replace(" ", "+")
    return datetime.fromisoformat(value)
