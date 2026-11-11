"""Run the full reproducible pathfinding experiment suite."""
from benchmark import run_benchmarks

if __name__ == "__main__":
    run_benchmarks(
        output_dir="results",
        sizes=(20, 50, 100),
        densities=(0.10, 0.30, 0.40),
        seeds=tuple(range(30)),  # 30 reproducible maze instances per setting
        repeats=7,               # median of 7 measured runs after one warm-up
    )
