from django.urls import path

from apps.network.views.nodes import NodeDetailView, NodeListCreateView
from apps.network.views.edges import EdgeDetailView, EdgeListCreateView
from apps.network.views.routes import ShortestRouteView

urlpatterns = [
    path("nodes", NodeListCreateView.as_view(), name="node-list-create"),
    path("nodes/<int:pk>", NodeDetailView.as_view(), name="node-detail"),
    path("edges", EdgeListCreateView.as_view(), name="edge-list-create"),
    path("edges/<int:pk>", EdgeDetailView.as_view(), name="edge-detail"),
    path("routes/shortest", ShortestRouteView.as_view(), name="route-shortest"),
]
