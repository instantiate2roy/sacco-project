from ..display import ContactOutcomeList, PaymentChannelList, PromiseStatusList
from .dashboard_section import DashboardSection
from .promises_due_plot import PromisesDuePlot
from .reachability_plot import ReachabilityPlot
from .treatments_started_plot import TreatmentsStartedPlot


class ActivitySection(DashboardSection):
    """
    What collections did in the period: treatments started, contacts made, payments received and promises due.
    """

    title = "Collections activity"
    plots = [TreatmentsStartedPlot, PromisesDuePlot, ReachabilityPlot]
    lists = [ContactOutcomeList, PaymentChannelList, PromiseStatusList]
