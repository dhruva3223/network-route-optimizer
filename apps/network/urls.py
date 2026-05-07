from django.urls import path

from apps.network.views.nodes import NodeDetailView, NodeListCreateView

urlpatterns = [
    path("nodes", NodeListCreateView.as_view(), name="node-list-create"),
    path("nodes/<int:pk>", NodeDetailView.as_view(), name="node-detail"),
]
