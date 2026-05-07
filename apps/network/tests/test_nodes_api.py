import json

from django.test import Client, TestCase

from apps.network.models import Node


class NodeApiTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_post_node_creates_and_returns_201(self):
        resp = self.client.post(
            "/api/network/nodes",
            data=json.dumps({"name": "ServerA"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        body = resp.json()
        self.assertIn("id", body)
        self.assertEqual(body["name"], "ServerA")
        self.assertTrue(Node.objects.filter(id=body["id"]).exists())

    def test_post_node_missing_name_returns_400(self):
        resp = self.client.post(
            "/api/network/nodes",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        body = resp.json()
        self.assertEqual(body, {"error": "Name missing or duplicate"})

    def test_post_node_duplicate_name_returns_400(self):
        Node.objects.create(name="ServerA")
        resp = self.client.post(
            "/api/network/nodes",
            data=json.dumps({"name": "ServerA"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        body = resp.json()
        self.assertEqual(body, {"error": "Name missing or duplicate"})

    def test_get_nodes_returns_200_list(self):
        Node.objects.create(name="ServerA")
        Node.objects.create(name="ServerB")
        resp = self.client.get("/api/network/nodes")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("nodes", body)
        self.assertEqual({n["name"] for n in body["nodes"]}, {"ServerA", "ServerB"})

    def test_delete_node_returns_204(self):
        node = Node.objects.create(name="ServerA")
        resp = self.client.delete(f"/api/network/nodes/{node.id}")
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Node.objects.filter(id=node.id).exists())

