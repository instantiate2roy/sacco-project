from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from .dashboard_view import DashboardView
from .error import ExportError


class ReportExporter(ABC):
    """Saves a dashboard view to files in a folder named after its business date."""

    extension = ""

    def __init__(self, folder: str | Path = "export"):
        self.folder = Path(folder)

    @abstractmethod
    def export(self, view: DashboardView) -> list[Path]:
        """Write the view and return the files created."""

    def _target(self, view: DashboardView, name: str) -> Path:
        """export/<date>/<name>_<filters>_<time>.<ext>; the time stops a file being overwritten."""
        folder = self.folder / f"{view.business_date:%Y-%m-%d}"
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise ExportError(f"Can't create the export folder {folder}: {error}") from error
        filters = "_".join(v.replace(" ", "-") for v in view.filters.values() if v != "All") or "all"
        return folder / f"{name}_{filters}_{datetime.now():%H%M%S}.{self.extension}"
