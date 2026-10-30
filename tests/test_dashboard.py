import matplotlib.pyplot as plt
import pandas as pd
import pytest

from src.dashboard import (ActivitySection, BalanceProjectionPlot, ComplianceSection, CsvExporter, DashboardExport,
                           DashboardFilters, DashboardPlot, ExportError, HeadlineSection, LoansByBucketPlot,
                           ParTrendPlot, PdfExporter, PortfolioAtRiskSection, PortfolioDashboard, ProfileBalancePlot,
                           ProjectionSection, PromisesDuePlot, ReachabilityPlot, RiskSection, TierBalancePlot,
                           TopLoansSection, TreatmentsStartedPlot, WriteOffProjectionPlot)
from src.dashboard.exporters import exporter_for

ALL_PLOTS = [ParTrendPlot, LoansByBucketPlot, TierBalancePlot, ProfileBalancePlot, TreatmentsStartedPlot,
             PromisesDuePlot, ReachabilityPlot, BalanceProjectionPlot, WriteOffProjectionPlot]
ALL_SECTIONS = [HeadlineSection, PortfolioAtRiskSection, RiskSection, ActivitySection, ComplianceSection,
                ProjectionSection, TopLoansSection]


@pytest.fixture(scope="module")
def latest(pipeline):
    return pipeline.dashboard.view()


@pytest.fixture(scope="module")
def earlier(pipeline):
    return pipeline.dashboard.view(pipeline.dashboard.dates[-3])


def test_latest_view_covers_todays_loans(pipeline, latest):
    assert latest.business_date == pd.Timestamp(pipeline.as_of)
    assert latest.summary["loans"] == len(pipeline.today) == len(latest.loans)
    assert latest.summary["outstanding"] == int(pipeline.today["outstanding_balance"].sum())
    assert latest.buckets["loans_by_dpd"].sum() == len(pipeline.today)
    assert latest.loans["expected_loss"].is_monotonic_decreasing


def test_latest_view_has_the_compliance_run_and_projection(pipeline, latest):
    blocked = int((~pipeline.decisions["allowed"]).sum())
    assert latest.compliance["blocked"].sum() == blocked
    assert latest.notes["compliance"].startswith(f"{len(pipeline.decisions)} treatments proposed")
    assert "projection" not in latest.notes
    assert len(latest.projection) == 13
    assert latest.write_offs["months ahead"].tolist() == [3, 6, 12]


def test_earlier_dates_explain_what_is_missing(earlier):
    assert earlier.compliance.empty and earlier.projection.empty and earlier.write_offs.empty
    assert earlier.notes["compliance"].startswith("Compliance checks are only recorded")
    assert earlier.notes["projection"].startswith("The roll-rate projection is only shown")


def test_filters_narrow_every_table(pipeline):
    view = pipeline.dashboard.view(bucket="90+")
    assert set(view.loans["bucket"]) == {"90+"}
    assert view.summary["loans"] == int((pipeline.today["bucket"] == "90+").sum())
    assert view.summary["PAR90 %"] == 100.0


def test_options_list_every_choice_with_all_first(pipeline):
    options = pipeline.dashboard.options()
    assert options["bucket"] == ["All", "current", "1-30", "31-60", "61-90", "90+"]
    assert options["business_date"][-1] == pd.Timestamp(pipeline.as_of)


def test_filters_work_out_the_view_once_per_change(pipeline, monkeypatch):
    filters = DashboardFilters(pipeline.dashboard)
    calls, seen = [], []
    real_view = pipeline.dashboard.view
    monkeypatch.setattr(pipeline.dashboard, "view", lambda *args: calls.append(args) or real_view(*args))
    filters.on_change(seen.append)
    filters.on_change(seen.append)

    filters.bucket.value = "1-30"

    assert len(calls) == 1 and len(seen) == 2
    assert seen[0] is seen[1] is filters.current_view()
    assert set(seen[0].loans["bucket"]) == {"1-30"}


@pytest.mark.parametrize("section", ALL_SECTIONS)
def test_every_section_renders_and_follows_the_filters(pipeline, section):
    filters = DashboardFilters(pipeline.dashboard)
    part = section(filters)
    part.widget()
    assert section.title in part._header.value
    assert ("<img" in part._charts.value) == bool(section.plots)

    filters.business_date.value = pipeline.dashboard.dates[-3]
    for table in part._lists:
        assert table.view is filters.current_view()


def test_section_notes_and_headline_cards(pipeline):
    filters = DashboardFilters(pipeline.dashboard)
    compliance, headline = ComplianceSection(filters), HeadlineSection(filters)
    compliance.widget(), headline.widget()
    assert "treatments proposed for the next start-of-day run" in compliance._header.value
    assert f"<b>{len(pipeline.today):,}</b>" in headline._header.value


def test_top_loans_list_pages_through_every_selected_loan(pipeline):
    part = TopLoansSection(DashboardFilters(pipeline.dashboard))
    part.widget()
    loans = part._lists[0]
    assert len(loans.frame) == len(pipeline.today)
    assert loans.page_count() == -(-len(pipeline.today) // 25)


@pytest.mark.parametrize("plot", ALL_PLOTS)
@pytest.mark.parametrize("which", ["latest", "earlier"])
def test_every_plot_draws_for_any_view(plot, which, request):
    view = request.getfixturevalue(which)
    figure, ax = plt.subplots()
    chart = plot(view)
    chart.render(ax)
    assert isinstance(chart, DashboardPlot) and ax.get_title() == chart.title
    plt.close(figure)


def test_promises_plot_title_shows_the_keep_rate(latest):
    assert f"keep rate {latest.summary['promise keep rate %']}%" in PromisesDuePlot(latest).title


def test_csv_export_writes_one_file_per_table(latest, tmp_path):
    paths = CsvExporter(tmp_path).export(latest)
    assert len(paths) == len(latest.tables())
    assert all(p.parent == tmp_path / f"{latest.business_date:%Y-%m-%d}" for p in paths)
    assert pd.read_csv(next(p for p in paths if p.name.startswith("loans_"))).shape[0] == len(latest.loans)


def test_pdf_export_writes_a_report(latest, tmp_path):
    [path] = PdfExporter(tmp_path).export(latest)
    assert path.suffix == ".pdf" and path.read_bytes().startswith(b"%PDF")


def test_export_file_names_carry_the_filters(pipeline, tmp_path):
    [path] = PdfExporter(tmp_path).export(pipeline.dashboard.view(bucket="90+"))
    assert path.name.startswith("dashboard_90+_")


def test_unknown_export_format_is_an_error():
    with pytest.raises(ExportError, match="Unsupported export format 'XLSX'"):
        exporter_for("XLSX")


def test_export_bar_reports_success_and_failure(pipeline, tmp_path, monkeypatch):
    bar = DashboardExport(DashboardFilters(pipeline.dashboard), folder=tmp_path)
    bar.format.value = "CSV"
    bar._export(None)
    assert bar.result.value.startswith("Saved 14 file(s)")

    def fail(*_):
        raise ExportError("disk full")
    monkeypatch.setattr("src.dashboard.dashboard_export.exporter_for", fail)
    bar._export(None)
    assert "Export failed: disk full" in bar.result.value


def test_portfolio_dashboard_builds_every_part(pipeline):
    dashboard = PortfolioDashboard(pipeline.dashboard)
    assert [type(part) for part in dashboard.parts] == ALL_SECTIONS
