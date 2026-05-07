import json

from django.test import Client, TestCase

from apps.network.models import Edge, Node


class EdgeApiTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def _post_edge(self, payload: dict):
        return self.client.post(
            "/api/network/edges",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_post_edge_creates_and_returns_201(self):
        Node.objects.create(name="ServerA")
        Node.objects.create(name="ServerB")

        resp = self._post_edge(
            {"source": "ServerA", "destination": "ServerB", "latency": 12.5}
        )
        self.assertEqual(resp.status_code, 201)
        body = resp.json()

        self.assertIn("id", body)
        self.assertEqual(body["source"], "ServerA")
        self.assertEqual(body["destination"], "ServerB")
        self.assertAlmostEqual(body["latency"], 12.5)
        self.assertTrue(
            Edge.objects.filter(id=body["id"], latency=12.5).exists()
        )

    def test_post_edge_missing_source_destination_returns_400(self):
        Node.objects.create(name="ServerA")
        Node.objects.create(name="ServerB")

        resp = self._post_edge({"latency": 12.5})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {"error": "Source/destination missing"})

    def test_post_edge_latency_must_be_positive_returns_400(self):
        Node.objects.create(name="ServerA")
        Node.objects.create(name="ServerB")

        for latency in [0, -1]:
            resp = self._post_edge(
                {"source": "ServerA", "destination": "ServerB", "latency": latency}
            )
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(resp.json(), {"error": "Latency must be > 0"})

    def test_post_edge_nodes_not_found_returns_400(self):
        Node.objects.create(name="ServerA")

        resp = self._post_edge(
            {"source": "ServerA", "destination": "ServerB", "latency": 1.0}
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {"error": "Nodes not found"})

    def test_post_edge_duplicate_returns_400(self):
        a = Node.objects.create(name="ServerA")
        b = Node.objects.create(name="ServerB")
        Edge.objects.create(source=a, destination=b, latency=1.2)

        resp = self._post_edge(
            {"source": "ServerA", "destination": "ServerB", "latency": 2.3}
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {"error": "Duplicate edge"})

    def test_get_edges_returns_200_list(self):
        a = Node.objects.create(name="ServerA")
        b = Node.objects.create(name="ServerB")
        c = Node.objects.create(name="ServerC")
        Edge.objects.create(source=a, destination=b, latency=1.2)
        Edge.objects.create(source=b, destination=c, latency=2.3)

        resp = self.client.get("/api/network/edges")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("edges", body)
        self.assertEqual(len(body["edges"]), 2)

    def test_delete_edge_returns_204(self):
        a = Node.objects.create(name="ServerA")
        b = Node.objects.create(name="ServerB")
        edge = Edge.objects.create(source=a, destination=b, latency=1.2)

        resp = self.client.delete(f"/api/network/edges/{edge.id}")
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Edge.objects.filter(id=edge.id).exists())

    def test_delete_missing_edge_returns_404(self):
        resp = self.client.delete("/api/network/edges/999")
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json(), {"error": "Edge not found"})

