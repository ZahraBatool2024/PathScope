"""Run history: every search that is run is saved automatically.

Records are kept in memory (for the Performance Analysis page) and appended
to ``results/run_history.csv`` so they survive a restart.
"""
from __future__ import annotations

import csv
from pathlib import Path

HISTORY_FILE = Path("results") / "run_history.csv"

FIELDS = [
    "run_id", "timestamp", "algorithm", "strategy", "grid", "wall_pct",
    "maze_id", "status", "path_cost", "steps", "nodes_expanded",
    "nodes_generated", "expanded_pct", "runtime_ms", "optimal",
]
_NUMERIC_INT = {"run_id", "nodes_expanded", "nodes_generated"}
_NUMERIC_FLOAT = {"wall_pct", "expanded_pct", "runtime_ms"}


class RunHistory:
    """Ordered list of completed runs, oldest first."""

    def __init__(self, path: Path = HISTORY_FILE) -> None:
        self.path = Path(path)
        self.records: list[dict] = []
        self._load()

    # ---- persistence -----------------------------------------------------
    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            with self.path.open(newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    rec: dict = {}
                    for key in FIELDS:
                        value = row.get(key, "")
                        if key in _NUMERIC_INT:
                            value = int(value)
                        elif key in _NUMERIC_FLOAT:
                            value = float(value)
                        rec[key] = value
                    self.records.append(rec)
        except (OSError, ValueError, KeyError):
            self.records = []  # Corrupt file: start clean rather than crash.

    def _append_to_disk(self, record: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        new_file = not self.path.exists() or self.path.stat().st_size == 0
        with self.path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            if new_file:
                writer.writeheader()
            writer.writerow(record)

    # ---- public API ------------------------------------------------------
    def add(self, record: dict) -> dict:
        record = {key: record.get(key, "") for key in FIELDS}
        record["run_id"] = (self.records[-1]["run_id"] + 1) if self.records else 1
        self.records.append(record)
        try:
            self._append_to_disk(record)
        except OSError:
            pass  # Never let a disk problem break the experiment itself.
        return record

    def clear(self) -> None:
        self.records.clear()
        try:
            self.path.unlink(missing_ok=True)
        except OSError:
            pass

    def newest_first(self) -> list[dict]:
        return list(reversed(self.records))

    def latest_for_maze(self, maze_id: str) -> dict[str, dict]:
        """Most recent run of each algorithm on one maze."""
        latest: dict[str, dict] = {}
        for rec in self.records:
            if rec["maze_id"] == maze_id:
                latest[rec["algorithm"]] = rec
        return latest

    def to_csv_text(self) -> str:
        import io
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(self.records)
        return buffer.getvalue()
