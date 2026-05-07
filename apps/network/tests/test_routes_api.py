import json

from django.test import Client, TestCase

from apps.network.models import Edge, Node, RouteQuery


class RoutesApiTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def _post_shortest(self, payload: dict):
        return self.client.post(
            "/api/network/routes/shortest",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_post_shortest_path_returns_200_and_persists_route(self):
        a = Node.objects.create(name="ServerA")
        b = Node.objects.create(name="ServerB")
        d = Node.objects.create(name="ServerD")
        Edge.objects.create(source=a, destination=b, latency=5.0)
        Edge.objects.create(source=b, destination=d, latency=7.0)

        resp = self._post_shortest({"source": "ServerA", "destination": "ServerD"})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()

        self.assertEqual(body["total_latency"], 12.0)
        self.assertEqual(body["path"], ["ServerA", "ServerB", "ServerD"])

        self.assertEqual(RouteQuery.objects.count(), 1)
        route = RouteQuery.objects.get()
        self.assertEqual(route.source, a)
        self.assertEqual(route.destination, d)
        self.assertEqual(route.total_latency, 12.0)
        self.assertEqual(route.path, ["ServerA", "ServerB", "ServerD"])

    def test_post_shortest_no_path_returns_404(self):
        Node.objects.create(name="ServerA")
        Node.objects.create(name="ServerD")

        resp = self._post_shortest({"source": "ServerA", "destination": "ServerD"})
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(
            resp.json(),
            {"error": "No path exists between ServerA and ServerD"},
        )

    def test_post_shortest_invalid_nodes_returns_400(self):
        Node.objects.create(name="ServerA")

        resp = self._post_shortest({"source": "ServerA", "destination": "ServerX"})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {"error": "Invalid or non-existent nodes"})

    def test_post_shortest_missing_source_or_destination_returns_400(self):
        resp = self._post_shortest({"source": "ServerA"})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {"error": "Invalid or non-existent nodes"})

        resp = self._post_shortest({"destination": "ServerD"})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {"error": "Invalid or non-existent nodes"})

    def test_post_shortest_tie_breaks_lexicographically(self):
        # Two equal shortest routes:
        # A-B-D (total 10) and A-C-D (total 10).
        a = Node.objects.create(name="ServerA")
        b = Node.objects.create(name="ServerB")
        c = Node.objects.create(name="ServerC")
        d = Node.objects.create(name="ServerD")

        Edge.objects.create(source=a, destination=b, latency=3.0)
        Edge.objects.create(source=b, destination=d, latency=7.0)
        Edge.objects.create(source=a, destination=c, latency=3.0)
        Edge.objects.create(source=c, destination=d, latency=7.0)

        resp = self._post_shortest({"source": "ServerA", "destination": "ServerD"})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["total_latency"], 10.0)
        self.assertEqual(body["path"], ["ServerA", "ServerB", "ServerD"])

