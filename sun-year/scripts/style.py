"""Shared matplotlib style for sun charts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

# Semantic palette
COLORS = {
    "sunrise": "#D97706",
    "sunset": "#B91C1C",
    "noon": "#0F766E",
    "day": "#0D9488",
    "twilight": "#6366F1",
    "accent": "#2563EB",
    "extrema": "#059669",
    "grid": "#E7E5E4",
    "spine": "#D6D3D1",
    "text": "#1C1917",
    "muted": "#78716C",
    "bg": "#FAFAF9",
    "fill_warm": "#FED7AA",
    "fill_cool": "#A5F3FC",
}

MONTH_CMAP = "YlOrRd"
SERIES_COLORS = [COLORS["sunrise"], COLORS["noon"], COLORS["sunset"], COLORS["twilight"]]

# Layout constants
FIGSIZE_WIDE = (11.0, 5.8)
FIGSIZE_TALL = (11.0, 8.2)
FIGSIZE_SQUARE = (7.5, 7.5)
DPI = 150
LINE_WIDTH = 2.0
MARKER_SIZE = 36


def apply_base_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.labelsize": 11,
            "axes.labelcolor": COLORS["text"],
            "axes.edgecolor": COLORS["spine"],
            "axes.facecolor": COLORS["bg"],
            "figure.facecolor": COLORS["bg"],
            "figure.dpi": DPI,
            "savefig.dpi": DPI,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "xtick.color": COLORS["muted"],
            "ytick.color": COLORS["muted"],
            "text.color": COLORS["text"],
            "grid.color": COLORS["grid"],
            "grid.linestyle": "-",
            "grid.linewidth": 0.8,
            "grid.alpha": 1.0,
            "legend.frameon": False,
            "legend.fontsize": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "lines.linewidth": LINE_WIDTH,
        }
    )


def new_figure(
    nrows: int = 1,
    ncols: int = 1,
    *,
    figsize: tuple[float, float] | None = None,
    sharex: bool = False,
    sharey: bool = False,
) -> tuple[Figure, Any]:
    """Create a figure with base style applied. figsize defaults by panel count."""
    apply_base_style()
    if figsize is None:
        figsize = FIGSIZE_TALL if nrows * ncols > 1 else FIGSIZE_WIDE
    fig, ax = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=figsize,
        sharex=sharex,
        sharey=sharey,
        constrained_layout=True,
    )
    fig.patch.set_facecolor(COLORS["bg"])
    return fig, ax


def style_axes(ax: Axes, *, grid: bool = True, spines: bool = True) -> None:
    ax.set_facecolor(COLORS["bg"])
    if grid:
        ax.grid(True, axis="both")
        ax.set_axisbelow(True)
    if spines:
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.spines["left"].set_color(COLORS["spine"])
        ax.spines["bottom"].set_color(COLORS["spine"])
    else:
        for spine in ax.spines.values():
            spine.set_visible(False)


def month_axis(ax: Axes) -> None:
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.set_xlabel("")


def ref_hline(ax: Axes, y: float) -> None:
    ax.axhline(y, color=COLORS["accent"], ls="--", lw=1.0, alpha=0.65)


def ref_vline(ax: Axes, x: Any) -> None:
    ax.axvline(x, color=COLORS["accent"], ls=":", lw=1.0, alpha=0.5)


def mark_extrema(ax: Axes, x: Any, y: float) -> None:
    ax.scatter([x], [y], s=MARKER_SIZE, color=COLORS["extrema"], zorder=5, edgecolors="none")


def plot_line(
    ax: Axes,
    x: Any,
    y: Any,
    *,
    color: Any,
    label: str | None = None,
    lw: float = LINE_WIDTH,
    alpha: float = 1.0,
) -> None:
    ax.plot(x, y, color=color, lw=lw, label=label, alpha=alpha, solid_capstyle="round")


def place_legend(ax: Axes, *, ncol: int = 1, side: str = "right") -> None:
    """Legend fully outside the axes so it never covers the data."""
    if side == "top":
        ax.legend(
            loc="lower center",
            bbox_to_anchor=(0.5, 1.04),
            borderaxespad=0.0,
            ncol=ncol,
            frameon=False,
            columnspacing=1.0,
            handlelength=1.6,
        )
    else:
        ax.legend(
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            borderaxespad=0.0,
            ncol=ncol,
            frameon=False,
            handlelength=1.6,
        )


def month_colors(n: int) -> np.ndarray:
    cmap = plt.get_cmap(MONTH_CMAP)
    return cmap(np.linspace(0.25, 0.95, n))


def save_figure(fig: Figure, path: Path, *, dpi: int = DPI) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # pad_inches keeps outside legends inside the saved frame
    fig.savefig(
        path,
        dpi=dpi,
        facecolor=fig.get_facecolor(),
        bbox_inches="tight",
        pad_inches=0.25,
    )
    plt.close(fig)
