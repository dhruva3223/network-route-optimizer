from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from apps.network.models import Edge, Node, RouteQuery


class NetworkModelsTestCase(TestCase):
    def test_node_name_is_unique(self):
        Node.objects.create(name="ServerA")
        with self.assertRaises(IntegrityError):
            Node.objects.create(name="ServerA")

    def test_edge_latency_must_be_positive(self):
        a = Node.objects.create(name="ServerA")
        b = Node.objects.create(name="ServerB")

        edge = Edge(source=a, destination=b, latency=0)
        with self.assertRaises(ValidationError):
            edge.full_clean()

    def test_edge_source_destination_is_unique(self):
        a = Node.objects.create(name="ServerA")
        b = Node.objects.create(name="ServerB")

        Edge.objects.create(source=a, destination=b, latency=1.2)
        with self.assertRaises(IntegrityError):
            Edge.objects.create(source=a, destination=b, latency=2.3)

    def test_route_query_persists_path(self):
        a = Node.objects.create(name="ServerA")
        b = Node.objects.create(name="ServerB")
        route = RouteQuery.objects.create(
            source=a,
            destination=b,
            total_latency=12.5,
            path=["ServerA", "ServerB"],
        )
        self.assertEqual(route.path, ["ServerA", "ServerB"])

