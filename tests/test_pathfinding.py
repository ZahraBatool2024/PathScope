import random
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from algorithms import MinHeap, astar, dijkstra
from history import RunHistory
from maze import (bottleneck_walls, default_endpoints, generate_maze,
                  generate_reachable_maze, has_path, random_walls,
                  spiral_walls, validate_path)


class MinHeapTests(unittest.TestCase):
    def test_pops_in_sorted_order(self):
        rng = random.Random(1)
        values = [rng.random() for _ in range(2000)]
        heap = MinHeap()
        for v in values:
            heap.push(v)
        self.assertEqual([heap.pop() for _ in values], sorted(values))
        self.assertFalse(heap)

    def test_tuple_items_and_empty_pop(self):
        heap = MinHeap()
        heap.push((2, 0, "b"))
        heap.push((1, 1, "a"))
        self.assertEqual(heap.pop()[2], "a")
        heap.pop()
        with self.assertRaises(IndexError):
            heap.pop()

    def test_algorithms_do_not_use_heapq(self):
        source = (Path(__file__).resolve().parent.parent / "algorithms.py").read_text()
        self.assertNotIn("import heapq", source)
        self.assertNotIn("heappush", source)


class PathfindingTests(unittest.TestCase):
    def test_empty_obstacle_free_grid(self):
        grid = [[0] * 8 for _ in range(8)]
        for fn in (astar, dijkstra):
            result = fn(grid, (0, 0), (7, 7))
            self.assertTrue(result.success)
            self.assertEqual(result.path_cost, 14)
            self.assertTrue(validate_path(grid, result.path, (0, 0), (7, 7)))

    def test_guaranteed_generator_always_connected(self):
        for seed in range(30):
            grid = generate_reachable_maze(30, 30, 0.4, seed)
            self.assertTrue(has_path(grid, (0, 0), (29, 29)))

    def test_algorithms_agree_on_random_grids(self):
        for seed in range(60):
            grid = generate_maze(25, 25, 0.3, seed)
            d, a = dijkstra(grid, (0, 0), (24, 24)), astar(grid, (0, 0), (24, 24))
            self.assertEqual(d.success, a.success)
            self.assertEqual(d.success, has_path(grid, (0, 0), (24, 24)))
            if d.success:
                self.assertEqual(d.path_cost, a.path_cost)
                self.assertTrue(validate_path(grid, a.path, (0, 0), (24, 24)))
                self.assertTrue(validate_path(grid, d.path, (0, 0), (24, 24)))

    def test_custom_start_and_goal(self):
        grid = random_walls(20, 0.25, 7, keep_free=((3, 12), (15, 2)))
        d, a = dijkstra(grid, (3, 12), (15, 2)), astar(grid, (3, 12), (15, 2))
        self.assertEqual(d.success, a.success)
        if d.success:
            self.assertEqual(d.path_cost, a.path_cost)

    def test_unreachable_goal(self):
        grid = [[0] * 5 for _ in range(5)]
        for r, c in ((3, 4), (4, 3)):
            grid[r][c] = 1
        for fn in (astar, dijkstra):
            result = fn(grid, (0, 0), (4, 4))
            self.assertFalse(result.success)
            self.assertIsNone(result.path)

    def test_start_equals_goal(self):
        for fn in (astar, dijkstra):
            result = fn([[0]], (0, 0), (0, 0))
            self.assertTrue(result.success)
            self.assertEqual(result.path_cost, 0)

    def test_astar_expands_no_more_than_dijkstra_on_open_grid(self):
        grid = [[0] * 20 for _ in range(20)]
        self.assertLess(astar(grid, (4, 4), (16, 16)).expanded_nodes,
                        dijkstra(grid, (4, 4), (16, 16)).expanded_nodes)

    def test_blocked_endpoint_rejected(self):
        grid = [[0, 1], [0, 0]]
        with self.assertRaises(ValueError):
            astar(grid, (0, 0), (0, 1))


class PresetTests(unittest.TestCase):
    def test_presets_keep_endpoints_free(self):
        for size in (10, 20, 30):
            start, goal = default_endpoints(size)
            for grid in (random_walls(size, .4, 3, (start, goal)),
                         spiral_walls(size, (start, goal)),
                         bottleneck_walls(size, (start, goal))):
                self.assertEqual(grid[start[0]][start[1]], 0)
                self.assertEqual(grid[goal[0]][goal[1]], 0)
                self.assertEqual(len(grid), size)


class HistoryTests(unittest.TestCase):
    def test_records_persist_and_reload(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run_history.csv"
            h = RunHistory(path)
            h.add({"algorithm": "A* (Manhattan)", "maze_id": "abc123", "nodes_expanded": 10,
                   "nodes_generated": 12, "wall_pct": 5.0, "expanded_pct": 2.5,
                   "runtime_ms": 0.1, "path_cost": 8, "status": "Path found"})
            h.add({"algorithm": "Dijkstra", "maze_id": "abc123", "nodes_expanded": 40,
                   "nodes_generated": 44, "wall_pct": 5.0, "expanded_pct": 10.0,
                   "runtime_ms": 0.4, "path_cost": 8, "status": "Path found"})
            self.assertEqual([r["run_id"] for r in h.newest_first()], [2, 1])
            reloaded = RunHistory(path)
            self.assertEqual(len(reloaded.records), 2)
            self.assertEqual(set(reloaded.latest_for_maze("abc123")), {"A* (Manhattan)", "Dijkstra"})
            reloaded.clear()
            self.assertFalse(path.exists())
            self.assertEqual(reloaded.records, [])

    def test_only_runs_that_happened_are_listed(self):
        with tempfile.TemporaryDirectory() as tmp:
            h = RunHistory(Path(tmp) / "h.csv")
            self.assertEqual(h.newest_first(), [])
            h.add({"algorithm": "Dijkstra", "maze_id": "m1", "nodes_expanded": 1,
                   "nodes_generated": 1, "wall_pct": 0.0, "expanded_pct": 1.0, "runtime_ms": 0.1})
            self.assertEqual({r["algorithm"] for r in h.records}, {"Dijkstra"})


if __name__ == "__main__":
    unittest.main()
