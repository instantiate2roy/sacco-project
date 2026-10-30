from pathlib import Path

from .csv_exporter import CsvExporter
from .error import ExportError
from .pdf_exporter import PdfExporter
from .report_exporter import ReportExporter

EXPORTERS = {"CSV": CsvExporter, "PDF": PdfExporter}


def exporter_for(format_name: str, folder: str | Path = "export") -> ReportExporter:
    if format_name not in EXPORTERS:
        raise ExportError(f"Unsupported export format '{format_name}'; choose one of {', '.join(EXPORTERS)}")
    return EXPORTERS[format_name](folder)
