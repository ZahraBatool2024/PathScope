<div align="center">
  
# PathScope — Grid Pathfinding Analyzer
</div>

PathScope is an interactive grid-based pathfinding visualizer built with Python and NiceGUI. It demonstrates how A* Search and Dijkstra's Algorithm navigate through obstacles to find an optimal path between a starting point and a goal.
Both algorithms and their binary min-heap priority queue are implemented from scratch without using external pathfinding libraries.
<div align="center">
  
## Features
</div>

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
\
f(n)=g(n)+h(n)


#### Dijkstra's Algorithm
Dijkstra's Algorithm expands the node with the smallest accumulated path cost:
\
f(n)=g(n)


It provides an optimal-path baseline for comparison with A*.


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

<div align="center">
  
## Technology Stack

</div>

| Technology | Purpose |
|---|---|
| Python | Core application and algorithm implementation |
| NiceGUI | Interactive web interface |
| HTML/CSS/SVG | Interface styling and grid visualization |
| Python Standard Library | Data structures, timing, CSV storage, and utility operations |

<div align="center">
  
## Installation and Setup

</div>

### 1. Clone the repository

```bash
git clone https://github.com/ZahraBatool2024/PathScope.git
cd PathScope
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

**Windows:**

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Run the application

```bash
python app.py
```

## Running Tests

Run the unit tests using:

```bash
python -m unittest discover -s tests -v
```

The tests cover the search algorithms and supporting functionality, including path validity, maze reachability, and history management.

<div align="center">
  
## Project Objective

</div>

The objective of PathScope is to provide an interactive environment for understanding and evaluating classical graph search algorithms.

By combining from-scratch algorithm implementations with real-time visualization and automatic experiment tracking, PathScope makes it easier to observe how different search strategies explore a maze and discover optimal paths.

<div align="center">
  
## Future Improvements

</div>

- Add Breadth-First Search and Greedy Best-First Search.
- Support weighted grids and configurable movement costs.
- Introduce additional heuristic functions.
- Add more maze-generation techniques.
- Improve performance visualization and experiment reporting.

<div align="center">
  
## Author

**Zahra Batool**

 **GitHub:** [ZahraBatool2024](https://github.com/ZahraBatool2024)
 
 **LinkedIn:** [Zahra Batool](https://www.linkedin.com/in/zahra-batool-94673a31a)

---

*PathScope — Visualize search, explore algorithms, and understand pathfinding performance.*
</div>
