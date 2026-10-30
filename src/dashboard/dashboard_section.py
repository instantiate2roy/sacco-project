import base64
import html
import io

import ipywidgets as widgets
import matplotlib.pyplot as plt
from IPython.display import display

from ..plot import Plot
from .dashboard_filters import DashboardFilters
from .dashboard_view import DashboardView


class DashboardSection:
    """
    One part of the dashboard, shown in its own cell and redrawn whenever the shared filters change.

    Subclasses set the title and list what the section holds: its charts (DashboardPlot classes,
    drawn side by side) and its tables (DashboardList classes from src/display, shown below them).
    The charts are an image held in a widget and replaced on each change, rather than display()
    calls captured by an Output widget, so they render once in every notebook frontend.
    """

    title: str = "Section"
    plots: list = []               # DashboardPlot classes
    lists: list = []               # DashboardList classes
    note: str = ""                 # which of the view's notes to show, if any (compliance, projection)

    def __init__(self, filters: DashboardFilters):
        self.filters = filters
        view = filters.current_view()
        self._header = widgets.HTML()
        self._charts = widgets.HTML()
        self._lists = [table(view) for table in self.lists]
        filters.on_change(self._refresh)

    def header(self, view: DashboardView) -> str:
        """
        The section's title and note, as HTML; a subclass can add to it.
        """
        note = view.notes.get(self.note) if self.note else None
        return (f"<h3 style='margin:0 0 8px 0'>{html.escape(self.title)}</h3>"
                + (f"<p>{html.escape(note)}</p>" if note else ""))

    def widget(self) -> widgets.VBox:
        self._refresh(self.filters.current_view())
        return widgets.VBox([self._header, self._charts, *[table.widget() for table in self._lists]])

    def show(self) -> None:
        display(self.widget())

    def _refresh(self, view: DashboardView) -> None:
        self._header.value = self.header(view)
        self._charts.value = self._charts_html(view) if self.plots else ""
        for table in self._lists:
            table.update(view)

    # an ordinary method, not a staticmethod: %autoreload drops the staticmethod wrapper when it adds
    # a new method to a class already loaded in the kernel
    def _charts_html(self, view: DashboardView) -> str:
        figure = Plot.row_figure(*[plot(view) for plot in self.plots])
        image = io.BytesIO()
        figure.savefig(image, format="png", dpi=80)
        plt.close(figure)
        encoded = base64.b64encode(image.getvalue()).decode("ascii")
        return f"<img src='data:image/png;base64,{encoded}' style='max-width:100%'>"
