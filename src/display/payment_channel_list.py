from .dashboard_list import DashboardList


class PaymentChannelList(DashboardList):
    """
    Posted payments received in the period, by channel.
    """

    title = "Payments received in the period"
    columns = ["channel", "payments", "amount"]
    sort_by = ["amount"]
    sort_ascending = False

    def table(self, view):
        return view.payments
