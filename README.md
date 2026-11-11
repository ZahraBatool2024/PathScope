# PathScope — Grid Pathfinding Analyzer

A pure-Python web app for visualising and comparing **A\* (Manhattan)** and
**Dijkstra** on a four-directional, unit-cost grid. No HTML/JavaScript to write:
the whole site (UI, board drawing, animation, analytics) is Python, built with
[NiceGUI](https://nicegui.io).

## Run it
```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py                   # opens http://localhost:8080
```

## Pages
**Search Simulator** — one screen, no scrolling. Paint walls, move the start /
goal, load presets (Random, Spiral Trap, Bottleneck), pick an algorithm, set the
animation speed and press *Run Search*. Live metrics: path cost, steps, nodes
explored, expanded density, execution time.

**Performance Analysis** — every run is recorded automatically (in memory and in
`results/run_history.csv`). Only algorithms that were actually run appear. When
both algorithms have been run on the same maze, a head-to-head strip compares
them. *Download CSV* exports the history; *Clear History* resets it.

## Project layout
| File | Purpose |
|---|---|
| `app.py` | The website (NiceGUI) |
| `algorithms.py` | A\*, Dijkstra and a binary min-heap — **all written from scratch** (no `heapq`) |
| `maze.py` | Maze generators, presets, BFS reachability oracle, path validator |
| `history.py` | Automatic run history + CSV persistence |
| `benchmark.py`, `main.py`, `visualize_results.py` | Original batch-experiment tooling (unchanged) |
| `tests/` | Unit tests |

## Notes on the algorithms
* Grid: 0 = free, 1 = wall. Moves: up/down/left/right, cost 1.
* A\*: `f(n) = g(n) + h(n)`, `h` = Manhattan distance (admissible and consistent here).
  Ties on `f` are broken in favour of larger `g`.
* Dijkstra: `f(n) = g(n)`.
* The priority queue is `MinHeap` in `algorithms.py` (array-backed binary heap).
* Each run in the app is cross-checked against an independent BFS reachability
  test and a path validator. The reported runtime is the median of 5 repeats.

## Tests
```bash
python -m unittest discover -s tests -v
```

## Batch experiments (optional, unchanged)
```bash
python main.py
python visualize_results.py
```
