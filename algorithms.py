"""A* and Dijkstra search, implemented completely from scratch.

Nothing here comes from a library: the priority queue is a hand-written
binary min-heap (``MinHeap``), and both searches are written directly on top
of it.

Grid conventions:
    0 = walkable cell
    1 = blocked cell
Positions are (row, column). Movement is up/down/left/right with cost 1.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, asdict
from typing import Optional

Position = tuple[int, int]
Grid = list[list[int]]


# --------------------------------------------------------------------------
# Data structure: binary min-heap (priority queue), written from scratch
# --------------------------------------------------------------------------
class MinHeap:
    """Array-backed binary min-heap.

    Items are compared with ``<``, so tuples such as ``(priority, tie, node)``
    work naturally. push/pop are O(log n); peeking at the minimum is O(1).
    """

    def __init__(self) -> None:
        self._items: list = []

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    def push(self, item) -> None:
        items = self._items
        items.append(item)
        child = len(items) - 1
        # Sift up: move the new item towards the root while it is smaller
        # than its parent.
        while child > 0:
            parent = (child - 1) // 2
            if items[child] < items[parent]:
                items[child], items[parent] = items[parent], items[child]
                child = parent
            else:
                break

    def pop(self):
        items = self._items
        if not items:
            raise IndexError("pop from an empty MinHeap")
        smallest = items[0]
        last = items.pop()
        if items:
            items[0] = last
            size = len(items)
            parent = 0
            # Sift down: move the item towards the leaves while a child is
            # smaller than it.
            while True:
                left = 2 * parent + 1
                right = left + 1
                best = parent
                if left < size and items[left] < items[best]:
                    best = left
                if right < size and items[right] < items[best]:
                    best = right
                if best == parent:
                    break
                items[parent], items[best] = items[best], items[parent]
                parent = best
        return smallest


# --------------------------------------------------------------------------
# Result container
# --------------------------------------------------------------------------
@dataclass
class SearchResult:
    algorithm: str
    path: Optional[list[Position]]
    path_cost: Optional[int]
    runtime_ms: float
    expanded_nodes: int
    generated_nodes: int
    success: bool
    expanded_order: list[Position] = None

    def to_dict(self) -> dict:
        data = asdict(self)
        if self.path is not None:
            data["path"] = [list(p) for p in self.path]
        return data


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def _neighbors(grid: Grid, node: Position):
    """Yield walkable four-directional neighbors."""
    rows, cols = len(grid), len(grid[0])
    r, c = node
    for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
            yield (nr, nc)


def _reconstruct_path(came_from: dict[Position, Position],
                      start: Position,
                      goal: Position) -> list[Position]:
    path = [goal]
    while path[-1] != start:
        path.append(came_from[path[-1]])
    path.reverse()
    return path


def _validate_input(grid: Grid, start: Position, goal: Position) -> None:
    if not grid or not grid[0]:
        raise ValueError("Grid must be non-empty.")
    if any(len(row) != len(grid[0]) for row in grid):
        raise ValueError("Grid must be rectangular.")
    rows, cols = len(grid), len(grid[0])
    for name, (r, c) in (("start", start), ("goal", goal)):
        if not (0 <= r < rows and 0 <= c < cols):
            raise ValueError(f"{name} position {(r, c)} is outside the grid.")
        if grid[r][c] != 0:
            raise ValueError(f"{name} position {(r, c)} is blocked.")


def manhattan(a: Position, b: Position) -> int:
    """Admissible, consistent heuristic for 4-directional unit-cost movement."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# --------------------------------------------------------------------------
# Dijkstra
# --------------------------------------------------------------------------
def dijkstra(grid: Grid, start: Position, goal: Position) -> SearchResult:
    """Dijkstra's algorithm: always expand the cheapest known node, f(n) = g(n).

    Uses unit-cost moves, so it is also the optimal-path baseline.
    """
    _validate_input(grid, start, goal)
    t0 = time.perf_counter()

    if start == goal:
        elapsed = (time.perf_counter() - t0) * 1000
        return SearchResult("Dijkstra", [start], 0, elapsed, 0, 1, True, [start])

    order = 0  # insertion counter: breaks ties between equal priorities
    frontier = MinHeap()
    frontier.push((0, order, start))
    distance = {start: 0}
    came_from: dict[Position, Position] = {}
    expanded = 0
    generated = 1
    expanded_order: list[Position] = []

    while frontier:
        cost, _, current = frontier.pop()
        if cost != distance.get(current):
            continue  # Outdated queue entry: a cheaper route was found later.

        expanded += 1
        expanded_order.append(current)
        if current == goal:
            path = _reconstruct_path(came_from, start, goal)
            elapsed = (time.perf_counter() - t0) * 1000
            return SearchResult("Dijkstra", path, cost, elapsed,
                                expanded, generated, True, expanded_order)

        for neighbor in _neighbors(grid, current):
            new_cost = cost + 1
            if new_cost < distance.get(neighbor, float("inf")):
                if neighbor not in distance:
                    generated += 1
                distance[neighbor] = new_cost
                came_from[neighbor] = current
                order += 1
                frontier.push((new_cost, order, neighbor))

    elapsed = (time.perf_counter() - t0) * 1000
    return SearchResult("Dijkstra", None, None, elapsed,
                        expanded, generated, False, expanded_order)


# --------------------------------------------------------------------------
# A* (Manhattan)
# --------------------------------------------------------------------------
def astar(grid: Grid, start: Position, goal: Position) -> SearchResult:
    """A* search using f(n) = g(n) + h(n), with h = Manhattan distance."""
    _validate_input(grid, start, goal)
    t0 = time.perf_counter()

    if start == goal:
        elapsed = (time.perf_counter() - t0) * 1000
        return SearchResult("A*", [start], 0, elapsed, 0, 1, True, [start])

    order = 0
    frontier = MinHeap()
    frontier.push((manhattan(start, goal), 0, order, start))
    g_score = {start: 0}
    came_from: dict[Position, Position] = {}
    expanded = 0
    generated = 1
    expanded_order: list[Position] = []

    while frontier:
        _, neg_g, _, current = frontier.pop()
        current_g = -neg_g  # g is stored negated for the tie-break below.
        if current_g != g_score.get(current):
            continue  # Outdated queue entry.

        expanded += 1
        expanded_order.append(current)
        if current == goal:
            path = _reconstruct_path(came_from, start, goal)
            elapsed = (time.perf_counter() - t0) * 1000
            return SearchResult("A*", path, current_g, elapsed,
                                expanded, generated, True, expanded_order)

        for neighbor in _neighbors(grid, current):
            tentative_g = current_g + 1
            if tentative_g < g_score.get(neighbor, float("inf")):
                if neighbor not in g_score:
                    generated += 1
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                f_score = tentative_g + manhattan(neighbor, goal)
                order += 1
                # Ties on f are broken by larger g (deeper nodes first), then
                # by insertion order, which keeps A* focused on the goal.
                frontier.push((f_score, -tentative_g, order, neighbor))

    elapsed = (time.perf_counter() - t0) * 1000
    return SearchResult("A*", None, None, elapsed,
                        expanded, generated, False, expanded_order)
