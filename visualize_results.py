"""Generate publication-friendly benchmark charts from exported CSV files."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

RESULTS = Path("results")


def plot_metric(df: pd.DataFrame, metric: str, title: str, ylabel: str,
                filename: str, mode: str, successful_only: bool = False) -> None:
    data = df[df["experiment_mode"] == mode].copy()
    if successful_only and metric in {"median_runtime_ms_all", "median_runtime_ms_successful"}:
        metric = "median_runtime_ms_successful"
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for algorithm in ("Dijkstra", "A*"):
        for density in sorted(data["obstacle_density_requested"].unique()):
            part = data[(data.algorithm == algorithm) &
                        (data.obstacle_density_requested == density)].sort_values("rows")
            ax.plot(part.rows, part[metric], marker="o", linewidth=2,
                    label=f"{algorithm} | obstacles {density:.0%}")
    ax.set(title=f"{title}\n({mode.replace('_', ' ').title()})",
           xlabel="Grid size (rows × columns)", ylabel=ylabel)
    ax.set_xticks(sorted(data.rows.unique()))
    ax.grid(True, alpha=.25); ax.legend(fontsize=8, ncol=2)
    fig.tight_layout(); fig.savefig(RESULTS / filename, dpi=220); plt.close(fig)


def main() -> None:
    summary_path = RESULTS / "benchmark_summary.csv"
    if not summary_path.exists():
        raise FileNotFoundError("Run python main.py before generating charts.")
    df = pd.read_csv(summary_path)
    for mode, prefix in (("random", "random"), ("guaranteed_reachable", "reachable")):
        plot_metric(df, "mean_expanded_nodes_successful", "Mean expanded nodes — successful trials",
                    "Mean expanded nodes", f"{prefix}_expanded_nodes_successful.png", mode)
        plot_metric(df, "median_runtime_ms_successful", "Median runtime — successful trials",
                    "Median runtime (ms)", f"{prefix}_runtime_successful.png", mode)
        plot_metric(df, "success_rate_pct", "Successful trial rate", "Success rate (%)",
                    f"{prefix}_success_rate.png", mode)
        plot_metric(df, "unsuccess_rate_pct", "Unsuccessful trial rate", "Unsuccessful rate (%)",
                    f"{prefix}_unsuccess_rate.png", mode)
        plot_metric(df, "mean_expanded_nodes_unsuccessful", "Mean expanded nodes — unsuccessful trials",
                    "Mean expanded nodes", f"{prefix}_expanded_nodes_unsuccessful.png", mode)
        plot_metric(df, "median_runtime_ms_unsuccessful", "Median runtime — unsuccessful trials",
                    "Median runtime (ms)", f"{prefix}_runtime_unsuccessful.png", mode)
        plot_metric(df, "mean_path_cost_successful", "Mean optimal path cost — successful trials",
                    "Mean path cost (moves)", f"{prefix}_path_cost.png", mode)
    print(f"All charts saved in: {RESULTS.resolve()}")

if __name__ == "__main__":
    main()
