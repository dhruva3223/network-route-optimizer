from django.contrib import admin

from apps.network.models import Edge, Node, RouteQuery


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]


@admin.register(Edge)
class EdgeAdmin(admin.ModelAdmin):
    list_display = ["id", "source", "destination", "latency"]
    list_filter = ["source", "destination"]


@admin.register(RouteQuery)
class RouteQueryAdmin(admin.ModelAdmin):
    list_display = ["id", "source", "destination", "total_latency", "created_at"]
    list_filter = ["source", "destination", "created_at"]
    search_fields = ["path"]

