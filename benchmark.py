"""Reproducible A* vs Dijkstra benchmark with repeated timing and two maze modes."""
from __future__ import annotations

import csv
import json
import statistics
import time
from pathlib import Path
from typing import Callable

from algorithms import astar, dijkstra
from maze import (count_walkable, generate_maze, generate_reachable_maze,
                  has_path, validate_path)

ALGORITHMS: tuple[tuple[str, Callable], ...] = (("Dijkstra", dijkstra), ("A*", astar))


def _measure(search_fn: Callable, grid: list[list[int]], start: tuple[int, int],
             goal: tuple[int, int], repeats: int) -> tuple[object, list[float]]:
    """Warm up once, then collect independent timings; return last result + times."""
    search_fn(grid, start, goal)  # warm-up excluded from timing samples
    samples: list[float] = []
    result = None
    for _ in range(repeats):
        result = search_fn(grid, start, goal)
        samples.append(result.runtime_ms)
    return result, samples


def _write_csv(path: Path, records: list[dict]) -> None:
    if not records:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def run_benchmarks(output_dir: str = "results", sizes: tuple[int, ...] = (20,  50, 100),
                   densities: tuple[float, ...] = (0.10, 0.30, 0.40),
                   seeds: tuple[int, ...] = tuple(range(30)), repeats: int = 7) -> list[dict]:
    if repeats < 3:
        raise ValueError("Use at least 3 timing repeats; 5–7 is recommended.")
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    raw: list[dict] = []
    logs: list[dict] = []
    generators = (("random", generate_maze), ("guaranteed_reachable", generate_reachable_maze))

    for mode, generator in generators:
        for size in sizes:
            for density in densities:
                for seed in seeds:
                    grid = generator(size, size, density, seed)
                    start, goal = (0, 0), (size-1, size-1)
                    walkable = count_walkable(grid)
                    expected_reachable = has_path(grid, start, goal)
                    maze_id = f"{mode}_{size}x{size}_d{density:.2f}_s{seed}"
                    maze_results = {}
                    for name, fn in ALGORITHMS:
                        result, samples = _measure(fn, grid, start, goal, repeats)
                        if result.success != expected_reachable:
                            raise AssertionError(f"{name} reachability mismatch: {maze_id}")
                        if result.success:
                            if not validate_path(grid, result.path, start, goal):
                                raise AssertionError(f"Invalid path from {name}: {maze_id}")
                            if result.path_cost != len(result.path)-1:
                                raise AssertionError(f"Path cost mismatch: {maze_id}")
                        record = {
                            "maze_id": maze_id, "experiment_mode": mode,
                            "algorithm": name, "rows": size, "cols": size,
                            "obstacle_density_requested": density,
                            "obstacle_density_actual": round(1-walkable/(size*size), 6),
                            "seed": seed, "walkable_cells": walkable,
                            "success": bool(result.success),
                            "path_cost": result.path_cost,
                            "path_length_cells": len(result.path) if result.path else None,
                            "runtime_ms": round(statistics.median(samples), 6),
                            "runtime_median_ms": round(statistics.median(samples), 6),
                            "runtime_mean_ms": round(statistics.mean(samples), 6),
                            "runtime_std_ms": round(statistics.stdev(samples), 6) if len(samples)>1 else 0.0,
                            "timing_repeats": repeats,
                            "expanded_nodes": result.expanded_nodes,
                            "generated_nodes": result.generated_nodes,
                            "expanded_node_density_pct": round(100*result.expanded_nodes/walkable, 6) if walkable else 0.0,
                        }
                        raw.append(record); maze_results[name] = result
                        logs.append({**record, "start": list(start), "goal": list(goal),
                                     "path": [list(p) for p in result.path] if result.path else None,
                                     "runtime_samples_ms": samples})
                    d, a = maze_results["Dijkstra"], maze_results["A*"]
                    if d.success != a.success or (d.success and d.path_cost != a.path_cost):
                        raise AssertionError(f"A* and Dijkstra disagree: {maze_id}")
        print(f"Completed {mode} experiments for {size}x{size} grids")

    _write_csv(out / "benchmark_results.csv", raw)
    with (out / "run_logs.json").open("w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)

    summary: list[dict] = []
    keys = ("experiment_mode", "rows", "obstacle_density_requested", "algorithm")
    groups: dict[tuple, list[dict]] = {}
    for row in raw:
        groups.setdefault(tuple(row[k] for k in keys), []).append(row)
    for key, group in sorted(groups.items()):
        successful = [r for r in group if r["success"]]
        failed = [r for r in group if not r["success"]]
        summary.append({
            **dict(zip(keys, key)), "trials": len(group),
            "successful_trials": len(successful), "unsuccessful_trials": len(failed),
            "success_rate_pct": round(100*len(successful)/len(group), 2),
            "unsuccess_rate_pct": round(100*len(failed)/len(group), 2),
            "median_runtime_ms_all": round(statistics.median(r["runtime_median_ms"] for r in group), 6),
            "median_runtime_ms_successful": round(statistics.median(r["runtime_median_ms"] for r in successful), 6) if successful else None,
            "median_runtime_ms_unsuccessful": round(statistics.median(r["runtime_median_ms"] for r in failed), 6) if failed else None,
            "mean_expanded_nodes_successful": round(statistics.mean(r["expanded_nodes"] for r in successful), 3) if successful else None,
            "mean_expanded_nodes_unsuccessful": round(statistics.mean(r["expanded_nodes"] for r in failed), 3) if failed else None,
            "median_expanded_nodes_successful": statistics.median(r["expanded_nodes"] for r in successful) if successful else None,
            "mean_path_cost_successful": round(statistics.mean(r["path_cost"] for r in successful), 3) if successful else None,
        })
    _write_csv(out / "benchmark_summary.csv", summary)
    print(f"\nBenchmark complete: {len(raw)} algorithm-maze records; {repeats} timing repeats each.")
    print(f"Detailed CSV: {(out/'benchmark_results.csv').resolve()}")
    print(f"Summary CSV:  {(out/'benchmark_summary.csv').resolve()}")
    print("Next: python visualize_results.py")
    return raw
