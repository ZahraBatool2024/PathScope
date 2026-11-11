"""PathScope - Grid Pathfinding Analyzer.

A pure-Python web app (NiceGUI) for visualising and comparing A* (Manhattan)
and Dijkstra on a four-directional, unit-cost grid. Both algorithms live in
``algorithms.py`` and are written from scratch.

Run with:  python app.py
"""
from __future__ import annotations

import hashlib
import random
import statistics
from datetime import datetime
from pathlib import Path

from nicegui import app, events, ui

from algorithms import SearchResult, astar, dijkstra
from history import RunHistory
from maze import (bottleneck_walls, count_walkable, default_endpoints,
                  empty_grid, has_path, random_walls, spiral_walls,
                  validate_path)

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
HISTORY = RunHistory(BASE_DIR / "results" / "run_history.csv")

APP_NAME = "PathScope"
APP_TAGLINE = "Grid Pathfinding Analyzer"
TAB_SIMULATOR = "Search Simulator"
TAB_ANALYSIS = "Performance Analysis"

VIEW = 600          # logical size of the board in SVG units
TIMING_REPEATS = 5  # reported runtime = median of this many runs

ALGORITHMS = {
    "astar": {"label": "A* Search \u2014 Manhattan", "name": "A* (Manhattan)",
              "strategy": "g(n) + h(n)", "fn": astar},
    "dijkstra": {"label": "Dijkstra's Algorithm", "name": "Dijkstra",
                 "strategy": "g(n)", "fn": dijkstra},
}

# Board colours (same palette as the original site)
C_OPEN, C_WALL, C_LINE = "#111827", "#475569", "#263449"
C_START, C_GOAL = "#10b981", "#f43f5e"
C_EXPLORED, C_FRONTIER, C_PATH = "#8b5cf6", "#06b6d4", "#f59e0b"

BLANK_BOARD = ("data:image/svg+xml;utf8,"
               f"<svg xmlns='http://www.w3.org/2000/svg' width='{VIEW}' height='{VIEW}'/>")

app.add_static_files("/assets", str(ASSETS_DIR))

PAGE_CSS = """
@layer overrides {
html, body { overflow: hidden !important; background: #0b0f19; }
body { font-family: 'Inter', sans-serif; }
.mono { font-family: 'JetBrains Mono', monospace; }
.nicegui-content { padding: 0 !important; gap: 0 !important; }
.q-page { min-height: 0 !important; }
.q-tab-panels, .q-panel, .q-tab-panel { background: transparent !important; padding: 0 !important; overflow: hidden !important; }

.app-header { height: 56px; padding: 0 20px; background: rgba(17,24,39,.88);
  border-bottom: 1px solid #1f2937; backdrop-filter: blur(10px); }
.brand-name { font-size: 1.1rem; font-weight: 800; letter-spacing: .02em; line-height: 1.1;
  background: linear-gradient(90deg,#60a5fa,#818cf8,#a78bfa); -webkit-background-clip: text;
  background-clip: text; color: transparent; }
.brand-sub { font-size: .68rem; color: #9ca3af; line-height: 1.1; }

.glass { background: rgba(17,24,39,.7); border: 1px solid rgba(255,255,255,.08); border-radius: 12px; }
.panel-title { font-size: .68rem; font-weight: 700; color: #9ca3af; text-transform: uppercase; letter-spacing: .08em; }

/* ---- Simulator: one screen, no page scrolling ---- */
.sim-root { display: flex; gap: 12px; padding: 12px; box-sizing: border-box; width: 100%;
  height: calc(100dvh - 56px); overflow: hidden; }
.sim-side { width: 272px; flex: none; display: flex; flex-direction: column; gap: 10px;
  overflow-y: auto; scrollbar-width: none; }
.sim-side::-webkit-scrollbar { display: none; }
.sim-main { flex: 1; min-width: 0; min-height: 0; display: flex; flex-direction: column; gap: 10px; }
.side-card { padding: 12px; display: flex; flex-direction: column; gap: 8px; flex: none; }
.toolbar { padding: 8px 12px; display: flex; flex-wrap: wrap; align-items: center; gap: 10px; flex: none; }
.stage { flex: 1; min-height: 0; padding: 10px 12px; display: flex; flex-direction: column; gap: 8px; }
.legend { display: flex; align-items: center; justify-content: space-between; font-size: .72rem;
  color: #9ca3af; flex: none; gap: 12px; }
.legend-items { display: flex; flex-wrap: wrap; gap: 4px 14px; align-items: center; }
.legend-items span { display: inline-flex; align-items: center; gap: 5px; white-space: nowrap; }
.sw { width: 10px; height: 10px; border-radius: 3px; display: inline-block; }
.board-wrap { flex: 1; min-height: 0; display: flex; align-items: center; justify-content: center; }
.board { height: 100%; aspect-ratio: 1 / 1; max-width: 100%; border: 1px solid #1f2937;
  border-radius: 8px; overflow: hidden; background: #0a0f1a; cursor: crosshair; }
.metrics { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; flex: none; }
.metric { padding: 7px 8px; text-align: center; }
.metric .k { font-size: .6rem; color: #9ca3af; text-transform: uppercase; letter-spacing: .08em; display: block; }
.metric .v { font-size: 1.05rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }

.q-btn.tool-btn { border: 1px solid #374151 !important; background: rgba(17,24,39,.5) !important;
  color: #9ca3af !important; border-radius: 8px !important; font-size: .75rem !important; min-height: 34px; }
.q-btn.tool-btn.on { border-color: color-mix(in srgb, var(--c) 55%, transparent) !important;
  background: color-mix(in srgb, var(--c) 14%, transparent) !important; color: var(--c) !important; }
.dot { width: 11px; height: 11px; border-radius: 50%; display: inline-block; margin-right: 6px; }
.q-btn.soft-btn { background: #1f2937 !important; color: #d1d5db !important; border: 1px solid #374151 !important;
  border-radius: 8px !important; font-size: .75rem !important; }
.q-btn.soft-btn:hover { background: #374151 !important; }
.q-btn.danger-btn:hover { background: rgba(127,29,29,.45) !important; color: #fca5a5 !important; }
.val { color: #60a5fa; font-family: 'JetBrains Mono', monospace; font-size: .75rem; }

/* ---- Analysis page ---- */
.ana-root { max-width: 1280px; margin: 0 auto; padding: 16px 20px; box-sizing: border-box;
  height: calc(100dvh - 56px); display: flex; flex-direction: column; gap: 12px; overflow: hidden; }
.ana-scroll { flex: 0 1 auto; min-height: 0; overflow: auto; }
.h2h { padding: 10px 14px; display: flex; flex-wrap: wrap; gap: 8px 28px; align-items: center; flex: none; }
.h2h .k { font-size: .62rem; text-transform: uppercase; letter-spacing: .08em; color: #9ca3af; display: block; }
.h2h .v { font-size: .85rem; font-weight: 600; color: #e5e7eb; }
.empty-state { text-align: center; color: #6b7280; padding: 56px 16px; }
.q-table thead th { font-size: .68rem; text-transform: uppercase; letter-spacing: .05em; color: #9ca3af; }
.q-table tbody td { font-family: 'JetBrains Mono', monospace; font-size: .75rem; }
}
"""

ui.add_head_html("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
""", shared=True)
ui.add_css(PAGE_CSS, shared=True)


def maze_signature(grid: list[list[int]], start, goal) -> str:
    """Short stable id for a maze + start/goal (used to group comparable runs)."""
    text = f"{start}{goal}" + "".join("".join(map(str, row)) for row in grid)
    return hashlib.sha1(text.encode()).hexdigest()[:6]


def timed_search(fn, grid, start, goal) -> SearchResult:
    """Run a search several times; report the median runtime of the repeats."""
    result = fn(grid, start, goal)
    samples = [result.runtime_ms]
    for _ in range(TIMING_REPEATS - 1):
        samples.append(fn(grid, start, goal).runtime_ms)
    result.runtime_ms = statistics.median(samples)
    return result


class PathScope:
    """One browser session: board state, controls and both pages."""

    def __init__(self, history: RunHistory) -> None:
        self.history = history
        self.size = 20
        self.start, self.goal = default_endpoints(self.size)
        self.grid = empty_grid(self.size)
        self.tool = "wall"
        self.algo_key = "astar"
        self.painting = False
        self.last_cell: tuple[int, int] | None = None
        # Visualisation overlay
        self.explored: list[tuple[int, int]] = []
        self.current: tuple[int, int] | None = None
        self.path: list[tuple[int, int]] = []
        # Animation
        self.animating = False
        self.trace: list[tuple[int, int]] = []
        self.step = 0
        self.batch = 1
        self.pending: SearchResult | None = None

    # ------------------------------------------------------------------ UI
    def build(self) -> None:
        ui.dark_mode(True)
        ui.colors(primary="#3b82f6")

        with ui.header().classes("app-header items-center justify-between"):
            with ui.row().classes("items-center gap-3 no-wrap"):
                ui.image("/assets/logo.svg").classes("w-9 h-9").props("no-spinner")
                with ui.column().classes("gap-0"):
                    ui.label(APP_NAME).classes("brand-name")
                    ui.label(f"{APP_TAGLINE} \u00b7 A* & Dijkstra").classes("brand-sub")
            with ui.tabs(value="sim").props(
                    "dense no-caps inline-label indicator-color=primary active-color=blue-4"
            ).classes("text-gray-400") as tabs:
                ui.tab("sim", label=TAB_SIMULATOR, icon="route")
                ui.tab("perf", label=TAB_ANALYSIS, icon="insights")

        with ui.tab_panels(tabs, value="sim").props("animated=false").classes("w-full"):
            with ui.tab_panel("sim"):
                self._build_simulator()
            with ui.tab_panel("perf"):
                self._build_analysis()

        self.timer = ui.timer(0.02, self._tick, active=False)
        self.set_tool("wall")
        self.render()

    # ---- simulator page --------------------------------------------------
    def _build_simulator(self) -> None:
        with ui.element("div").classes("sim-root"):
            with ui.element("div").classes("sim-side"):
                self._build_tools_card()
                self._build_setup_card()
                self._build_execution_card()
            with ui.element("div").classes("sim-main"):
                self._build_toolbar()
                self._build_stage()
                self._build_metrics()

    def _build_tools_card(self) -> None:
        with ui.element("div").classes("glass side-card"):
            ui.label("Brush Tools").classes("panel-title")
            with ui.element("div").classes("grid grid-cols-2 gap-2"):
                self.tool_buttons: dict[str, ui.button] = {}
                for key, label, color in (("start", "Start Node", C_START),
                                          ("goal", "Goal Node", C_GOAL),
                                          ("wall", "Wall", "#94a3b8"),
                                          ("erase", "Eraser", "#22d3ee")):
                    btn = ui.button(on_click=lambda k=key: self.set_tool(k)) \
                        .props("flat no-caps dense").classes("tool-btn").style(f"--c:{color}")
                    with btn:
                        ui.element("span").classes("dot").style(f"background:{color}")
                        ui.label(label)
                    self.tool_buttons[key] = btn

    def _build_setup_card(self) -> None:
        with ui.element("div").classes("glass side-card"):
            ui.label("Maze & Grid Setup").classes("panel-title")
            with ui.row().classes("w-full justify-between items-center no-wrap gap-0"):
                ui.label("Grid Size").classes("text-xs text-gray-300")
                self.size_label = ui.label("20 \u00d7 20").classes("val")
            self.size_slider = ui.slider(min=10, max=30, value=20, step=1) \
                .props("dense label color=blue-5")
            self.size_slider.on_value_change(
                lambda e: self.size_label.set_text(f"{int(e.value)} \u00d7 {int(e.value)}"))
            self.size_slider.on("change", lambda _: self.resize(int(self.size_slider.value)))

            with ui.row().classes("w-full justify-between items-center no-wrap gap-0"):
                ui.label("Random Obstacle Density").classes("text-xs text-gray-300")
                self.density_label = ui.label("30%").classes("val")
            self.density_slider = ui.slider(min=10, max=50, value=30, step=1) \
                .props("dense label color=blue-5")
            self.density_slider.on_value_change(
                lambda e: self.density_label.set_text(f"{int(e.value)}%"))

            ui.label("Preset Configurations").classes("text-xs text-gray-400")
            with ui.element("div").classes("grid grid-cols-3 gap-2"):
                for key, label in (("random", "Random"), ("spiral", "Spiral Trap"),
                                   ("bottleneck", "Bottleneck")):
                    ui.button(label, on_click=lambda k=key: self.load_preset(k)) \
                        .props("flat no-caps dense").classes("soft-btn")

    def _build_execution_card(self) -> None:
        with ui.element("div").classes("glass side-card"):
            ui.label("Execution Controls").classes("panel-title")
            with ui.row().classes("w-full justify-between items-center no-wrap gap-0"):
                ui.label("Animation Speed").classes("text-xs text-gray-300")
                self.speed_label = ui.label("Fast").classes("val")
            self.speed_slider = ui.slider(min=1, max=100, value=85, step=1) \
                .props("dense color=blue-5")
            self.speed_slider.on_value_change(self._on_speed)

    def _build_toolbar(self) -> None:
        with ui.element("div").classes("glass toolbar"):
            with ui.column().classes("gap-0"):
                ui.label("Algorithm").classes("panel-title")
                self.algo_select = ui.select(
                    {k: v["label"] for k, v in ALGORITHMS.items()}, value="astar",
                    on_change=lambda e: setattr(self, "algo_key", e.value),
                ).props("dense outlined dark options-dense").classes("w-60")
            ui.space()
            ui.button("Run Search", icon="play_arrow", on_click=self.run_search) \
                .props("no-caps unelevated color=primary").classes("font-semibold px-4")
            ui.button("Clear Path", on_click=self.clear_path) \
                .props("flat no-caps").classes("soft-btn")
            ui.button("Clear All", on_click=self.clear_all) \
                .props("flat no-caps").classes("soft-btn danger-btn")

    def _build_stage(self) -> None:
        with ui.element("div").classes("glass stage"):
            with ui.element("div").classes("legend"):
                with ui.element("div").classes("legend-items"):
                    for label, color in (("Start", C_START), ("Goal", C_GOAL), ("Wall", C_WALL),
                                         ("Frontier", C_FRONTIER), ("Explored", C_EXPLORED),
                                         ("Path", C_PATH)):
                        with ui.element("span"):
                            ui.element("i").classes("sw").style(f"background:{color}")
                            ui.html(label, sanitize=False)
                self.coord_label = ui.label("X: --, Y: --").classes("mono text-gray-500")
            with ui.element("div").classes("board-wrap"):
                self.board = ui.interactive_image(
                    BLANK_BOARD, size=(VIEW, VIEW), on_mouse=self._on_mouse,
                    events=["mousedown", "mousemove", "mouseup", "mouseleave"],
                    sanitize=False,
                ).classes("board")

    def _build_metrics(self) -> None:
        self.metric_labels: dict[str, ui.label] = {}
        with ui.element("div").classes("metrics"):
            for key, title, color in (("cost", "Path Cost", "#fbbf24"),
                                      ("steps", "Step Count", "#34d399"),
                                      ("explored", "Nodes Explored", "#818cf8"),
                                      ("density", "Expanded Density", "#38bdf8"),
                                      ("time", "Execution Time", "#c084fc")):
                with ui.element("div").classes("glass metric"):
                    ui.html(f"<span class='k'>{title}</span>", sanitize=False)
                    self.metric_labels[key] = ui.label("--").classes("v").style(f"color:{color}")

    # ---- analysis page ---------------------------------------------------
    def _build_analysis(self) -> None:
        with ui.element("div").classes("ana-root"):
            with ui.row().classes("w-full items-center justify-between no-wrap"):
                with ui.column().classes("gap-0"):
                    ui.label(TAB_ANALYSIS).classes("text-xl font-bold text-gray-100")
                    ui.label("Every search you run in the simulator is recorded here "
                             "automatically \u2014 algorithms that have not been run are not shown.") \
                        .classes("text-xs text-gray-400")
                with ui.row().classes("gap-2 no-wrap"):
                    ui.button("Download CSV", icon="download", on_click=self.download_csv) \
                        .props("flat no-caps").classes("soft-btn")
                    ui.button("Clear History", icon="delete_outline", on_click=self.confirm_clear) \
                        .props("flat no-caps").classes("soft-btn danger-btn")
            self.analysis_view()

    @ui.refreshable
    def analysis_view(self) -> None:
        records = self.history.newest_first()
        if not records:
            with ui.element("div").classes("glass empty-state w-full"):
                ui.icon("insights", size="40px").classes("text-gray-600")
                ui.label("No runs recorded yet").classes("text-base text-gray-300 mt-2")
                ui.label(f"Open the {TAB_SIMULATOR}, choose an algorithm and press Run Search. "
                         "Results will appear here automatically.").classes("text-sm")
            return

        current = self.history.latest_for_maze(maze_signature(self.grid, self.start, self.goal))
        if len(current) == 2:
            self._head_to_head(current["A* (Manhattan)"], current["Dijkstra"])

        columns = [
            {"name": "run_id", "label": "#", "field": "run_id", "align": "left", "sortable": True},
            {"name": "algorithm", "label": "Algorithm", "field": "algorithm", "align": "left", "sortable": True},
            {"name": "strategy", "label": "Strategy", "field": "strategy", "align": "left"},
            {"name": "maze", "label": "Maze (grid \u00b7 walls \u00b7 id)", "field": "maze", "align": "left"},
            {"name": "status", "label": "Status", "field": "status", "align": "left"},
            {"name": "path_cost", "label": "Path Cost (g)", "field": "path_cost", "align": "right", "sortable": True},
            {"name": "steps", "label": "Steps", "field": "steps", "align": "right"},
            {"name": "nodes_expanded", "label": "Nodes Explored", "field": "nodes_expanded", "align": "right", "sortable": True},
            {"name": "expanded_pct", "label": "Explored (%)", "field": "expanded_pct", "align": "right", "sortable": True},
            {"name": "runtime_ms", "label": "Runtime (ms)", "field": "runtime_ms", "align": "right", "sortable": True},
            {"name": "optimal", "label": "Optimal", "field": "optimal", "align": "center"},
        ]
        rows = [{**r, "maze": f'{r["grid"]} \u00b7 {r["wall_pct"]:.1f}% \u00b7 #{r["maze_id"]}'}
                for r in records]
        with ui.element("div").classes("glass ana-scroll"):
            table = ui.table(columns=columns, rows=rows, row_key="run_id",
                             pagination={"rowsPerPage": 0}) \
                .props("flat dense dark hide-bottom").classes("w-full bg-transparent")
            table.add_slot("body-cell-algorithm", """
                <q-td :props="props">
                  <span :class="props.value.startsWith('A') ? 'text-cyan-400' : 'text-violet-400'"
                        style="font-weight:600">{{ props.value }}</span>
                </q-td>""")
            table.add_slot("body-cell-status", """
                <q-td :props="props">
                  <q-badge :color="props.value === 'Path found' ? 'positive' : 'warning'"
                           :text-color="props.value === 'Path found' ? 'white' : 'black'"
                           :label="props.value" />
                </q-td>""")

    @staticmethod
    def _head_to_head(a: dict, d: dict) -> None:
        """Comparison strip shown only when both algorithms ran on this maze."""
        def compare(x: float, y: float) -> str:
            if not y or x == y:
                return "same for both"
            return (f"{abs(y - x) / y * 100:.1f}% fewer for A*" if x < y
                    else f"{abs(x - y) / y * 100:.1f}% more for A*")
        with ui.element("div").classes("glass h2h"):
            ui.html("<span class='k'>Head-to-head \u00b7 current maze</span>"
                    "<span class='v'>A* vs Dijkstra</span>", sanitize=False)
            ui.html("<span class='k'>Nodes explored</span><span class='v mono'>"
                    f"{a['nodes_expanded']} vs {d['nodes_expanded']} "
                    f"({compare(a['nodes_expanded'], d['nodes_expanded'])})</span>",
                    sanitize=False)
            ui.html("<span class='k'>Runtime</span><span class='v mono'>"
                    f"{a['runtime_ms']:.3f} ms vs {d['runtime_ms']:.3f} ms</span>", sanitize=False)
            same = str(a["path_cost"]) == str(d["path_cost"])
            ui.html("<span class='k'>Path cost</span><span class='v mono'>"
                    f"{a['path_cost'] if a['path_cost'] != '' else 'N/A'} vs "
                    f"{d['path_cost'] if d['path_cost'] != '' else 'N/A'} "
                    f"({'equal \u2713' if same else 'DIFFERENT'})</span>", sanitize=False)

    def download_csv(self) -> None:
        if not self.history.records:
            ui.notify("Nothing to download yet \u2014 run a search first.", type="info")
            return
        ui.download.content(self.history.to_csv_text(), "pathscope_results.csv", "text/csv")

    def confirm_clear(self) -> None:
        if not self.history.records:
            return
        with ui.dialog() as dialog, ui.card().classes("bg-gray-900"):
            ui.label("Delete all recorded runs?").classes("text-base font-semibold")
            ui.label("This also removes results/run_history.csv.").classes("text-xs text-gray-400")
            with ui.row().classes("justify-end w-full"):
                ui.button("Cancel", on_click=dialog.close).props("flat no-caps")
                ui.button("Delete", color="negative", on_click=lambda: (
                    self.history.clear(), self.analysis_view.refresh(), dialog.close()
                )).props("no-caps unelevated")
        dialog.open()

    # ------------------------------------------------------------ rendering
    def render(self) -> None:
        """Rebuild the board SVG from the current state."""
        n = self.size
        cs = VIEW / n

        def cell(r: int, c: int) -> str:
            return f'<rect x="{c * cs:.2f}" y="{r * cs:.2f}" width="{cs:.2f}" height="{cs:.2f}"/>'

        special = {self.start, self.goal}
        parts = [f'<rect width="{VIEW}" height="{VIEW}" fill="{C_OPEN}"/>']
        explored = "".join(cell(r, c) for r, c in self.explored if (r, c) not in special)
        if explored:
            parts.append(f'<g fill="{C_EXPLORED}">{explored}</g>')
        if self.current and self.current not in special:
            parts.append(f'<g fill="{C_FRONTIER}">{cell(*self.current)}</g>')
        path = "".join(cell(r, c) for r, c in self.path if (r, c) not in special)
        if path:
            parts.append(f'<g fill="{C_PATH}">{path}</g>')
        walls = "".join(cell(r, c) for r in range(n) for c in range(n) if self.grid[r][c])
        if walls:
            parts.append(f'<g fill="{C_WALL}">{walls}</g>')
        lines = "".join(f"M{i * cs:.2f} 0V{VIEW}M0 {i * cs:.2f}H{VIEW}" for i in range(n + 1))
        parts.append(f'<path d="{lines}" stroke="{C_LINE}" stroke-width="1" fill="none"/>')
        for (r, c), color, letter in ((self.start, C_START, "S"), (self.goal, C_GOAL, "G")):
            parts.append(f'<g fill="{color}">{cell(r, c)}</g>'
                         f'<text x="{(c + .5) * cs:.2f}" y="{(r + .5) * cs:.2f}" fill="#fff" '
                         f'font-family="Inter,Arial,sans-serif" font-weight="700" '
                         f'font-size="{cs * .55:.1f}" text-anchor="middle" '
                         f'dominant-baseline="central">{letter}</text>')
        self.board.content = "".join(parts)

    def set_metrics(self, **values: str) -> None:
        for key, label in self.metric_labels.items():
            label.set_text(values.get(key, "--"))

    # ------------------------------------------------------- board editing
    def set_tool(self, tool: str) -> None:
        self.tool = tool
        for key, btn in self.tool_buttons.items():
            btn.classes(add="on") if key == tool else btn.classes(remove="on")

    def _cell_from_event(self, e: events.MouseEventArguments) -> tuple[int, int] | None:
        cs = VIEW / self.size
        r, c = int(e.image_y // cs), int(e.image_x // cs)
        return (r, c) if 0 <= r < self.size and 0 <= c < self.size else None

    def _on_mouse(self, e: events.MouseEventArguments) -> None:
        if e.type == "mouseleave":
            self.painting = False
            self.last_cell = None
            self.coord_label.set_text("X: --, Y: --")
            return
        if e.type == "mouseup":
            self.painting = False
            return
        cell = self._cell_from_event(e)
        if cell is None:
            return
        if e.type == "mousedown":
            if self.animating:
                return
            self.painting = True
            self.last_cell = None
        if cell != self.last_cell:
            self.coord_label.set_text(f"X: {cell[1]}, Y: {cell[0]}")
            if self.painting and not self.animating:
                self.apply_tool(*cell)
            self.last_cell = cell

    def apply_tool(self, r: int, c: int) -> None:
        if self.tool == "start":
            if (r, c) == self.goal:
                return
            self.grid[r][c] = 0
            self.start = (r, c)
        elif self.tool == "goal":
            if (r, c) == self.start:
                return
            self.grid[r][c] = 0
            self.goal = (r, c)
        elif (r, c) in (self.start, self.goal):
            return
        elif self.tool == "wall":
            self.grid[r][c] = 1
        elif self.tool == "erase":
            self.grid[r][c] = 0
        self._reset_overlay()
        self.render()

    def _reset_overlay(self) -> None:
        self.explored, self.current, self.path = [], None, []

    def resize(self, size: int) -> None:
        self.stop_animation()
        self.size = size
        self.start, self.goal = default_endpoints(size)
        self.grid = empty_grid(size)
        self._reset_overlay()
        self.set_metrics()
        self.render()

    def load_preset(self, kind: str) -> None:
        self.stop_animation()
        self.start, self.goal = default_endpoints(self.size)
        keep = (self.start, self.goal)
        density = int(self.density_slider.value) / 100
        if kind == "random":
            self.grid = random_walls(self.size, density, random.randrange(10 ** 6), keep)
        elif kind == "spiral":
            self.grid = spiral_walls(self.size, keep)
        else:
            self.grid = bottleneck_walls(self.size, keep)
        self._reset_overlay()
        self.set_metrics()
        self.render()

    def clear_path(self) -> None:
        self.stop_animation()
        self._reset_overlay()
        self.set_metrics()
        self.render()

    def clear_all(self) -> None:
        self.stop_animation()
        self.start, self.goal = default_endpoints(self.size)
        self.grid = empty_grid(self.size)
        self._reset_overlay()
        self.set_metrics()
        self.render()

    # ---------------------------------------------------------- execution
    def _on_speed(self, e) -> None:
        v = int(e.value)
        self.speed_label.set_text("Slow Motion" if v < 30 else "Medium" if v <= 80
                                  else "Fast" if v < 90 else "Instant")

    def run_search(self) -> None:
        self.stop_animation()
        self._reset_overlay()
        algo = ALGORITHMS[self.algo_key]
        result = timed_search(algo["fn"], self.grid, self.start, self.goal)

        # Safety net: independent checks on every run.
        if result.success != has_path(self.grid, self.start, self.goal):
            raise AssertionError("Search disagrees with the BFS reachability check.")
        if result.success and not validate_path(self.grid, result.path, self.start, self.goal):
            raise AssertionError("Search returned an invalid path.")

        self._save_run(algo, result)

        self.trace = result.expanded_order or []
        speed = int(self.speed_slider.value)
        if not result.success:
            self.explored = list(self.trace)
            self.render()
            self._show_metrics(result)
            ui.notify("No path found \u2014 the goal is completely blocked.", type="warning")
            return
        if speed >= 90:
            self.explored, self.path = list(self.trace), list(result.path)
            self.render()
            self._show_metrics(result)
            return
        self.pending, self.step = result, 0
        self.batch = max(1, speed // 10)
        self.timer.interval = max(0.01, (100 - speed) / 1000)
        self.animating = True
        self.timer.activate()

    def _tick(self) -> None:
        if not self.animating:
            return
        total = len(self.trace)
        self.step = min(self.step + self.batch, total)
        self.explored = self.trace[:self.step]
        self.current = self.trace[self.step - 1] if 0 < self.step < total else None
        if self.step >= total:
            self.path = list(self.pending.path)
            self.stop_animation()
            self.render()
            self._show_metrics(self.pending)
            return
        self.render()

    def stop_animation(self) -> None:
        self.animating = False
        self.current = None
        if hasattr(self, "timer"):
            self.timer.deactivate()

    def _show_metrics(self, result: SearchResult) -> None:
        walkable = max(1, count_walkable(self.grid))
        ok = result.success
        self.set_metrics(
            cost=str(result.path_cost) if ok else "N/A",
            steps=str(len(result.path) - 1) if ok else "N/A",
            explored=str(result.expanded_nodes),
            density=f"{result.expanded_nodes / walkable * 100:.1f}%",
            time=f"{result.runtime_ms:.3f}ms",
        )

    def _save_run(self, algo: dict, result: SearchResult) -> None:
        """Automatically record every run (memory + results/run_history.csv)."""
        n = self.size
        walkable = max(1, count_walkable(self.grid))
        ok = result.success
        self.history.add({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "algorithm": algo["name"],
            "strategy": algo["strategy"],
            "grid": f"{n}\u00d7{n}",
            "wall_pct": round((1 - walkable / (n * n)) * 100, 1),
            "maze_id": maze_signature(self.grid, self.start, self.goal),
            "status": "Path found" if ok else "No path",
            "path_cost": result.path_cost if ok else "",
            "steps": len(result.path) - 1 if ok else "",
            "nodes_expanded": result.expanded_nodes,
            "nodes_generated": result.generated_nodes,
            "expanded_pct": round(result.expanded_nodes / walkable * 100, 2),
            "runtime_ms": round(result.runtime_ms, 4),
            "optimal": "Yes" if ok else "\u2014",
        })
        self.analysis_view.refresh()
        ui.notify(f"{algo['name'].split(' ')[0]} run saved", type="positive",
                  position="bottom-left", timeout=1200)


@ui.page("/")
def index() -> None:
    PathScope(HISTORY).build()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title=f"{APP_NAME} \u2014 {APP_TAGLINE}", favicon=ASSETS_DIR / "logo.svg",
           dark=True, reload=False, port=8080)
