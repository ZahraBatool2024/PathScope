"""Reproducible grid-maze generation and path validation.

Grid convention: 0 = free, 1 = obstacle. Movement is four-directional.
"""
from __future__ import annotations

import random
from collections import deque

Position = tuple[int, int]
Grid = list[list[int]]


def generate_maze(rows: int, cols: int, obstacle_density: float, seed: int) -> Grid:
    """Generate an unconstrained random maze; a route is not guaranteed."""
    _validate_generation_args(rows, cols, obstacle_density)
    rng = random.Random(seed)
    grid = [[int(rng.random() < obstacle_density) for _ in range(cols)] for _ in range(rows)]
    grid[0][0] = grid[-1][-1] = 0
    return grid


def generate_reachable_maze(rows: int, cols: int, obstacle_density: float, seed: int) -> Grid:
    """Generate a maze with a guaranteed route from top-left to bottom-right.

    A randomized monotonic route is carved first. Obstacles are then sampled
    from cells outside that route, up to the requested total obstacle count.
    Actual density can therefore be slightly below requested density.
    """
    _validate_generation_args(rows, cols, obstacle_density)
    rng = random.Random(seed)
    route = [(0, 0)]
    r = c = 0
    moves = ["down"] * (rows - 1) + ["right"] * (cols - 1)
    rng.shuffle(moves)
    for move in moves:
        if move == "down":
            r += 1
        else:
            c += 1
        route.append((r, c))
    protected = set(route)
    candidates = [(rr, cc) for rr in range(rows) for cc in range(cols)
                  if (rr, cc) not in protected]
    target_obstacles = min(round(rows * cols * obstacle_density), len(candidates))
    blocked = set(rng.sample(candidates, target_obstacles))
    return [[int((rr, cc) in blocked) for cc in range(cols)] for rr in range(rows)]


def _validate_generation_args(rows: int, cols: int, density: float) -> None:
    if rows < 1 or cols < 1:
        raise ValueError("rows and cols must be positive")
    if not 0.0 <= density < 1.0:
        raise ValueError("obstacle_density must be in [0, 1)")


def count_walkable(grid: Grid) -> int:
    return sum(cell == 0 for row in grid for cell in row)


def validate_path(grid: Grid, path: list[Position] | None,
                  start: Position, goal: Position) -> bool:
    if not path or path[0] != start or path[-1] != goal:
        return False
    rows, cols = len(grid), len(grid[0])
    for r, c in path:
        if not (0 <= r < rows and 0 <= c < cols) or grid[r][c] != 0:
            return False
    return all(abs(r1-r2) + abs(c1-c2) == 1
               for (r1, c1), (r2, c2) in zip(path, path[1:]))


def has_path(grid: Grid, start: Position, goal: Position) -> bool:
    """Independent BFS reachability oracle, used for validation only."""
    q = deque([start])
    seen = {start}
    rows, cols = len(grid), len(grid[0])
    while q:
        r, c = q.popleft()
        if (r, c) == goal:
            return True
        for nr, nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0 and (nr,nc) not in seen:
                seen.add((nr,nc)); q.append((nr,nc))
    return False


# --------------------------------------------------------------------------
# Interactive-app helpers (presets ported from the original web version)
# --------------------------------------------------------------------------
def empty_grid(size: int) -> Grid:
    """An obstacle-free square grid."""
    return [[0] * size for _ in range(size)]


def default_endpoints(size: int) -> tuple[Position, Position]:
    """Default start (20 %) and goal (80 %) positions along the diagonal."""
    return (int(size * 0.2), int(size * 0.2)), (int(size * 0.8), int(size * 0.8))


def random_walls(size: int, density: float, seed: int,
                 keep_free: tuple[Position, ...] = ()) -> Grid:
    """Random maze that keeps the given cells (start/goal) walkable."""
    grid = generate_maze(size, size, density, seed)
    for r, c in keep_free:
        grid[r][c] = 0
    return grid


def spiral_walls(size: int, keep_free: tuple[Position, ...] = ()) -> Grid:
    """'Spiral Trap' preset: concentric wall rings with a spiral corridor."""
    grid = empty_grid(size)
    top, bottom, left, right = 1, size - 2, 1, size - 2
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            grid[top][c] = 1
        top += 2
        for r in range(top, bottom + 1):
            grid[r][right] = 1
        right -= 2
        for c in range(right, left - 1, -1):
            if 0 <= bottom < size:
                grid[bottom][c] = 1
        bottom -= 2
        for r in range(bottom, top - 1, -1):
            if 0 <= left < size:
                grid[r][left] = 1
        left += 2
    for r, c in keep_free:
        grid[r][c] = 0
    return grid


def bottleneck_walls(size: int, keep_free: tuple[Position, ...] = ()) -> Grid:
    """'Bottleneck' preset: a vertical wall with a two-cell gap in the middle."""
    grid = empty_grid(size)
    mid_c, mid_r = size // 2, size // 2
    for r in range(size):
        if r not in (mid_r, mid_r - 1):
            grid[r][mid_c] = 1
    for r, c in keep_free:
        grid[r][c] = 0
    return grid
