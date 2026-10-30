from .activity_section import ActivitySection
from .compliance_section import ComplianceSection
from .dashboard_data import DashboardData
from .dashboard_export import DashboardExport
from .dashboard_filters import DashboardFilters
from .headline_section import HeadlineSection
from .portfolio_at_risk_section import PortfolioAtRiskSection
from .projection_section import ProjectionSection
from .risk_section import RiskSection
from .top_loans_section import TopLoansSection


class PortfolioDashboard:
    """
    The whole collections dashboard in one cell: the shared filters, every section, then the export bar.

    The notebook shows the sections in cells of their own instead; this is for seeing it all at once.
    """

    sections = [HeadlineSection, PortfolioAtRiskSection, RiskSection, ActivitySection, ComplianceSection,
                ProjectionSection, TopLoansSection]

    def __init__(self, data: DashboardData, export_folder: str = "export"):
        self.filters = DashboardFilters(data)
        self.parts = [section(self.filters) for section in self.sections]
        self.export = DashboardExport(self.filters, export_folder)

    def show(self) -> None:
        self.filters.show()
        for part in self.parts:
            part.show()
        self.export.show()
