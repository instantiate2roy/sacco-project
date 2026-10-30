import html

import ipywidgets as widgets
from IPython.display import display

from .dashboard_filters import DashboardFilters
from .error import ExportError
from .exporters import EXPORTERS, exporter_for


class DashboardExport:
    """
    An export bar that saves the view the dashboard filters select, as CSV files or a PDF report.
    """

    def __init__(self, filters: DashboardFilters, folder: str = "export"):
        self.filters = filters
        self.folder = folder
        self.format = widgets.Dropdown(description="Format", options=list(EXPORTERS), value="PDF",
                                       style={"description_width": "110px"})
        self.button = widgets.Button(description="Export", icon="download", button_style="primary")
        self.result = widgets.HTML()
        self.button.on_click(self._export)

    def show(self) -> None:
        display(widgets.VBox([widgets.HBox([self.format, self.button]), self.result]))

    def _export(self, _):
        try:
            paths = exporter_for(self.format.value, self.folder).export(self.filters.current_view())
        except ExportError as error:
            self.result.value = f"<span style='color:#cf222e'>Export failed: {html.escape(str(error))}</span>"
            return
        links = "".join(f"<li><a href='{html.escape(path.as_posix())}' target='_blank'>{html.escape(path.as_posix())}</a></li>"
                        for path in paths)
        self.result.value = f"Saved {len(paths)} file(s):<ul style='margin:4px 0'>{links}</ul>"
