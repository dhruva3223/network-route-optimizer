from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import gettext_lazy as _


class Node(models.Model):
    """Graph node (server)."""

    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Edge(models.Model):
    """Directed weighted edge between two nodes."""

    source = models.ForeignKey(
        Node, related_name="out_edges", on_delete=models.CASCADE
    )
    destination = models.ForeignKey(
        Node, related_name="in_edges", on_delete=models.CASCADE
    )
    latency = models.FloatField()

    class Meta:
        constraints = [
            UniqueConstraint(fields=["source", "destination"], name="unique_edge"),
            models.CheckConstraint(
                check=Q(latency__gt=0.0),
                name="edge_latency_gt_0",
            ),
        ]

    def clean(self) -> None:
        if self.latency is None:
            return
        if self.latency <= 0:
            raise ValidationError({"latency": _("latency must be > 0")})

    def __str__(self) -> str:
        return f"{self.source.name}->{self.destination.name} ({self.latency})"


class RouteQuery(models.Model):
    """Persisted shortest path queries for history endpoint."""

    source = models.ForeignKey(
        Node, related_name="routes_from", on_delete=models.CASCADE
    )
    destination = models.ForeignKey(
        Node, related_name="routes_to", on_delete=models.CASCADE
    )
    total_latency = models.FloatField()
    path = models.JSONField(help_text="List of node names representing the route.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["source", "destination", "created_at"]),
        ]

