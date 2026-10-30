from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

from .balance_projection_plot import BalanceProjectionPlot
from .dashboard_view import DashboardView
from .loans_by_bucket_plot import LoansByBucketPlot
from .par_trend_plot import ParTrendPlot
from .profile_balance_plot import ProfileBalancePlot
from .promises_due_plot import PromisesDuePlot
from .reachability_plot import ReachabilityPlot
from .report_exporter import ReportExporter
from .tier_balance_plot import TierBalancePlot
from .treatments_started_plot import TreatmentsStartedPlot
from .write_off_projection_plot import WriteOffProjectionPlot


class PdfExporter(ReportExporter):
    """A PDF report: the charts on the first page, then the main tables."""

    extension = "pdf"
    ROWS_PER_PAGE = 30
    PLOTS = [ParTrendPlot, LoansByBucketPlot, TierBalancePlot, ProfileBalancePlot, TreatmentsStartedPlot,
             PromisesDuePlot, ReachabilityPlot, BalanceProjectionPlot, WriteOffProjectionPlot]

    def export(self, view: DashboardView) -> list[Path]:
        path = self._target(view, "dashboard")
        with PdfPages(path) as pdf:
            figure = self._charts_page(view)
            pdf.savefig(figure)
            plt.close(figure)
            for title, table in [("Summary", pd.DataFrame([view.summary]).T.reset_index()
                                  .rename(columns={"index": "measure", 0: "value"})),
                                 ("Risk tiers", view.tiers), ("Profiles", view.profiles), ("Buckets", view.buckets),
                                 ("Projected new write-offs", view.write_offs),
                                 ("Contact outcomes", view.outcomes), ("Compliance blocks", view.compliance),
                                 ("Payments", view.payments), ("Promises", view.promises),
                                 ("Loans (highest expected loss first)", view.loans)]:
                self._table_pages(pdf, title, table, view)
        return [path]

    def _charts_page(self, view: DashboardView):
        """The dashboard's nine charts, three to a row, on one page."""
        figure, axes = plt.subplots(3, 3, figsize=(16, 12))
        for plot, ax in zip(self.PLOTS, axes.flat):
            plot(view).render(ax)
        figure.suptitle(f"Business date {view.business_date:%Y-%m-%d}", fontsize=13)
        figure.tight_layout()
        return figure

    def _table_pages(self, pdf: PdfPages, title: str, table: pd.DataFrame, view: DashboardView) -> None:
        if table.empty:
            table = pd.DataFrame({"note": ["nothing to show for these filters"]})
        table = table.copy()
        for column in table.select_dtypes("float").columns:
            table[column] = table[column].round(3)
        for start in range(0, len(table), self.ROWS_PER_PAGE):
            chunk = table.iloc[start:start + self.ROWS_PER_PAGE]
            figure, axis = plt.subplots(figsize=(11.7, 8.3))      # A4 landscape
            axis.axis("off")
            page = f" (rows {start + 1}-{start + len(chunk)} of {len(table)})" if len(table) > self.ROWS_PER_PAGE else ""
            axis.set_title(f"{title}{page} - business date {view.business_date:%Y-%m-%d}", loc="left")
            cells = axis.table(cellText=chunk.astype(str).values, colLabels=list(chunk.columns), loc="upper left")
            cells.auto_set_font_size(False)
            cells.set_fontsize(7)
            pdf.savefig(figure)
            plt.close(figure)
