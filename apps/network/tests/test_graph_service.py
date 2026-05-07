from django.test import SimpleTestCase

from apps.network.services.graph import EdgeWeight, dijkstra_shortest_path


class GraphServiceTestCase(SimpleTestCase):
    def test_shortest_path_basic(self):
        # A -> B -> D has total 2.0
        adjacency = {
            "A": [EdgeWeight(to="B", latency=1.0)],
            "B": [EdgeWeight(to="D", latency=1.0)],
            "D": [],
        }
        total, path = dijkstra_shortest_path(adjacency, "A", "D")
        self.assertEqual(total, 2.0)
        self.assertEqual(path, ["A", "B", "D"])

    def test_shortest_path_no_path_returns_none(self):
        adjacency = {
            "A": [EdgeWeight(to="B", latency=1.0)],
            "B": [],
            "D": [],
        }
        self.assertIsNone(dijkstra_shortest_path(adjacency, "A", "D"))

    def test_shortest_path_same_node_returns_zero_and_singleton_path(self):
        adjacency = {"A": []}
        total, path = dijkstra_shortest_path(adjacency, "A", "A")
        self.assertEqual(total, 0.0)
        self.assertEqual(path, ["A"])

    def test_shortest_path_disconnected_returns_none(self):
        # A and D are disconnected.
        adjacency = {
            "A": [EdgeWeight(to="B", latency=1.0)],
            "B": [],
            "C": [EdgeWeight(to="D", latency=1.0)],
            "D": [],
        }
        self.assertIsNone(dijkstra_shortest_path(adjacency, "A", "D"))

    def test_shortest_path_tie_break_lexicographically_smallest_path(self):
        # Two equal shortest routes:
        # A-B-D and A-C-D both total 2.0
        adjacency = {
            "A": [
                EdgeWeight(to="B", latency=1.0),
                EdgeWeight(to="C", latency=1.0),
            ],
            "B": [EdgeWeight(to="D", latency=1.0)],
            "C": [EdgeWeight(to="D", latency=1.0)],
            "D": [],
        }
        total, path = dijkstra_shortest_path(adjacency, "A", "D")
        self.assertEqual(total, 2.0)
        # Lexicographically smaller between ("A","B","D") and ("A","C","D")
        self.assertEqual(path, ["A", "B", "D"])

