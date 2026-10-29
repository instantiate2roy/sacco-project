from abc import ABC, abstractmethod
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure


class Plot(ABC):
    """
    One chart in the notebook.

    Subclasses only say what to draw, in draw(); Plot takes care of the figure, showing it,
    saving it to a file, and putting several charts side by side.
    """

    title: str = "Chart"
    xlabel: str = ""
    ylabel: str = ""
    size: tuple[float, float] = (5.5, 4)     # width and height in inches, for a chart on its own

    @abstractmethod
    def draw(self, ax: Axes) -> None:
        """
        Draw the chart's lines, bars or points onto `ax`.
        """

    def render(self, ax: Axes) -> None:
        """
        Draw the chart, then add its title and axis labels.
        """
        self.draw(ax)
        ax.set(title=self.title, xlabel=self.xlabel, ylabel=self.ylabel)

    def figure(self) -> Figure:
        """
        This chart on a figure of its own.
        """
        fig, ax = plt.subplots(figsize=self.size)
        self.render(ax)
        fig.tight_layout()
        return fig

    def show(self) -> None:
        """
        Draw the chart in the notebook
        """
        self.figure()
        plt.show()

    def save(self, path: str | Path) -> Path:
        """
        Save the chart as an image or PDF; the file type follows the extension
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig = self.figure()
        fig.savefig(path, dpi=150)
        plt.close(fig)
        return path

    @staticmethod
    def row_figure(*plots: "Plot", height: float = 4) -> Figure:
        """Several charts in one row on a single figure"""
        fig, axes = plt.subplots(1, len(plots), figsize=(5.5 * len(plots), height), squeeze=False)
        for plot, ax in zip(plots, axes[0]):
            plot.render(ax)
        fig.tight_layout()
        return fig

    @staticmethod
    def side_by_side(*plots: "Plot", height: float = 4) -> None:
        """Show several charts in one row"""
        Plot.row_figure(*plots, height=height)
        plt.show()