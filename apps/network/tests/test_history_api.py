from datetime import timedelta

from django.test import Client, TestCase
from django.utils import timezone

from apps.network.models import Node, RouteQuery


class RouteHistoryApiTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.a = Node.objects.create(name="ServerA")
        self.b = Node.objects.create(name="ServerB")
        self.c = Node.objects.create(name="ServerC")

        now = timezone.now()
        self.r1 = RouteQuery.objects.create(
            source=self.a,
            destination=self.b,
            total_latency=10.0,
            path=["ServerA", "ServerB"],
        )
        self.r2 = RouteQuery.objects.create(
            source=self.a,
            destination=self.c,
            total_latency=20.0,
            path=["ServerA", "ServerC"],
        )
        self.r3 = RouteQuery.objects.create(
            source=self.b,
            destination=self.c,
            total_latency=30.0,
            path=["ServerB", "ServerC"],
        )

        # Force timestamps to deterministic values for date filter tests.
        RouteQuery.objects.filter(id=self.r1.id).update(created_at=now - timedelta(days=2))
        RouteQuery.objects.filter(id=self.r2.id).update(created_at=now - timedelta(days=1))
        RouteQuery.objects.filter(id=self.r3.id).update(created_at=now)

    def test_history_returns_list(self):
        resp = self.client.get("/routes/history")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIsInstance(body, list)
        self.assertEqual(len(body), 3)
        self.assertIn("created_at", body[0])

    def test_history_filters_by_source(self):
        resp = self.client.get("/routes/history?source=ServerA")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual({r["destination"] for r in body}, {"ServerB", "ServerC"})

    def test_history_filters_by_destination(self):
        resp = self.client.get("/routes/history?destination=ServerC")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual({r["source"] for r in body}, {"ServerA", "ServerB"})

    def test_history_limit(self):
        resp = self.client.get("/routes/history?limit=1")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(len(body), 1)

    def test_history_date_from_to(self):
        now = timezone.now()
        date_from = (now - timedelta(days=1, hours=12)).isoformat()
        date_to = (now - timedelta(hours=12)).isoformat()

        resp = self.client.get(
            f"/routes/history?date_from={date_from}&date_to={date_to}"
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        # Only r2 falls between those bounds (roughly “yesterday”).
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["destination"], "ServerC")

    def test_history_invalid_limit_returns_400(self):
        resp = self.client.get("/routes/history?limit=abc")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.json())

    def test_history_invalid_datetime_returns_400(self):
        resp = self.client.get("/routes/history?date_from=not-a-datetime")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.json())

