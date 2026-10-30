from ..display import ComplianceBlockList
from .dashboard_section import DashboardSection


class ComplianceSection(DashboardSection):
    """
    The latest start-of-day run's compliance results for the selected loans.
    """

    title = "Compliance"
    note = "compliance"
    lists = [ComplianceBlockList]
