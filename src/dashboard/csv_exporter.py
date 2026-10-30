from pathlib import Path

from .dashboard_view import DashboardView
from .report_exporter import ReportExporter


class CsvExporter(ReportExporter):
    """One CSV file per dashboard table."""

    extension = "csv"

    def export(self, view: DashboardView) -> list[Path]:
        paths = []
        for name, table in view.tables().items():
            path = self._target(view, name)
            table.to_csv(path, index=False)
            paths.append(path)
        return paths
