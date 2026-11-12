# PathScope — Grid Pathfinding Analyzer

**An interactive Python web application for visualizing and analyzing A* and Dijkstra pathfinding algorithms implemented from scratch.**

PathScope is an interactive grid-based pathfinding visualizer built with Python and NiceGUI. It demonstrates how A* Search and Dijkstra's Algorithm navigate through obstacles to find an optimal path between a starting point and a goal.

The application provides an interactive maze editor, animated search visualization, and performance analysis. Users can create custom mazes, select a pathfinding algorithm, observe explored nodes, and examine search results such as execution time, path cost, and the number of expanded and generated nodes.

Both algorithms and their binary min-heap priority queue are implemented from scratch without using external pathfinding libraries.

## Features

### 1. Interactive Search Simulator

- Interactive grid-based maze editor.
- Set and reposition start and goal points.
- Draw and erase obstacles.
- Generate random mazes.
- Use predefined maze configurations:
  - Random Maze
  - Spiral Trap
  - Bottleneck
- Visualize explored nodes during the search process.
- Animate the final path.
- Adjust search animation speed.
- Reset and customize the maze for new experiments.

### 2. Pathfinding Algorithms

PathScope implements two classical graph search algorithms.

#### A* Search — Manhattan Heuristic

A* prioritizes nodes using the estimated total cost:

\[
f(n)=g(n)+h(n)
\]

Where:

- \(g(n)\) is the actual cost from the start node to the current node.
- \(h(n)\) is the estimated cost from the current node to the goal.
- \(f(n)\) is the estimated total path cost.

PathScope uses the Manhattan distance heuristic:

\[
h(n)=|r_n-r_g|+|c_n-c_g|
\]

This heuristic is appropriate for four-directional movement with uniform movement costs.

#### Dijkstra's Algorithm

Dijkstra's Algorithm expands the node with the smallest accumulated path cost:

\[
f(n)=g(n)
\]

It provides an optimal-path baseline for comparison with A*.

#### From-Scratch Implementation

Both algorithms are implemented in `algorithms.py`.

The implementation includes:

- A custom binary min-heap priority queue.
- Node expansion and neighbor exploration.
- Distance and cost tracking.
- Predecessor mapping.
- Path reconstruction.
- Search success and failure handling.
- Runtime measurement.
- Expanded and generated node tracking.

No external pathfinding library or built-in heap implementation is used.

### 3. Performance Analysis

PathScope automatically records completed searches in its run history.

The Performance Analysis page provides:

- Algorithm name and search strategy.
- Maze configuration and obstacle percentage.
- Search status.
- Execution time.
- Path cost.
- Path length.
- Expanded nodes.
- Generated nodes.
- Explored-node percentage.
- Optimality information.

When both algorithms have been executed on the same maze, their recorded results can be compared.

### 4. Automatic Experiment Tracking

Every completed search is automatically saved.

The application:

- Maintains search records during the application session.
- Saves records to `results/run_history.csv`.
- Loads previously saved records when the application restarts.
- Allows users to download the experiment history as a CSV file.
- Provides an option to clear the saved history.

Search execution time is measured using repeated runs, with the median of five measurements reported to reduce the effect of timing fluctuations.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application and algorithm implementation |
| NiceGUI | Interactive web interface |
| HTML/CSS/SVG | Interface styling and grid visualization |
| Python Standard Library | Data structures, timing, CSV storage, and utility operations |

## Project Structure

```text
PathScope/
│
├── assets/
│   └── logo.svg
│
├── results/
│   └── .gitkeep
│
├── tests/
│   └── test_pathfinding.py
│
├── app.py
├── algorithms.py
├── maze.py
├── history.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Main Files

| File | Description |
|---|---|
| `app.py` | Main NiceGUI application, interactive simulator, animation, and performance analysis |
| `algorithms.py` | From-scratch A* and Dijkstra implementations and custom binary min-heap |
| `maze.py` | Grid creation, obstacle generation, maze presets, reachability checks, and path validation |
| `history.py` | Automatic experiment history management and CSV export |
| `assets/logo.svg` | Application logo |
| `tests/test_pathfinding.py` | Unit tests for the pathfinding implementation and supporting modules |
| `results/` | Stores automatically generated search history |

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/PathScope.git
cd PathScope
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Run the application

```bash
python app.py
```

Open your browser and navigate to:

```text
http://localhost:8080
```

## Running Tests

Run the unit tests using:

```bash
python -m unittest discover -s tests -v
```

The tests cover the search algorithms and supporting functionality, including path validity, maze reachability, and history management.

## Project Objective

The objective of PathScope is to provide an interactive environment for understanding and evaluating classical graph search algorithms.

By combining from-scratch algorithm implementations with real-time visualization and automatic experiment tracking, PathScope makes it easier to observe how different search strategies explore a maze and discover optimal paths.

## Future Improvements

- Add Breadth-First Search and Greedy Best-First Search.
- Support weighted grids and configurable movement costs.
- Introduce additional heuristic functions.
- Add more maze-generation techniques.
- Improve performance visualization and experiment reporting.

## Author

**Zahra Batool**

BS Artificial Intelligence  
The Islamia University of Bahawalpur

- **GitHub:** [ZahraBatool2024](https://github.com/ZahraBatool2024)
- **LinkedIn:** [Zahra Batool](https://www.linkedin.com/in/zahra-batool-94673a31a)

---

*PathScope — Visualize search, explore algorithms, and understand pathfinding performance.*
