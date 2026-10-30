import ipywidgets as widgets
from IPython.display import display

from .dashboard_data import ALL, DashboardData
from .dashboard_view import DashboardView


class DashboardFilters:
    """
    The filters every dashboard section shares: business date, officer, profile, bucket and risk tier.

    Show them once, in their own cell; each section created with them redraws when one changes.
    The view is worked out once per change and shared, rather than once per section.
    """

    def __init__(self, data: DashboardData):
        self.data = data
        options = data.options()
        style = {"description_width": "110px"}
        self.business_date = widgets.Dropdown(
            description="Business date", options=[(f"{d:%Y-%m-%d}", d) for d in options["business_date"]],
            value=options["business_date"][-1], style=style)
        self.assigned_to = widgets.Dropdown(description="Officer", options=options["assigned_to"], value=ALL, style=style)
        self.profile = widgets.Dropdown(description="Profile", options=options["profile"], value=ALL, style=style)
        self.bucket = widgets.Dropdown(description="Bucket", options=options["bucket"], value=ALL, style=style)
        self.tier = widgets.Dropdown(description="Risk tier", options=options["tier"], value=ALL, style=style)
        self._widgets = [self.business_date, self.assigned_to, self.profile, self.bucket, self.tier]
        self._listeners = []
        self._view: DashboardView | None = None
        for widget in self._widgets:
            widget.observe(self._changed, names="value")

    def current_view(self) -> DashboardView:
        """
        The dashboard view for the filters as they are now.
        """
        if self._view is None:
            self._view = self.data.view(self.business_date.value, self.assigned_to.value, self.profile.value,
                                        self.bucket.value, self.tier.value)
        return self._view

    def on_change(self, listener) -> None:
        """
        Call listener(view) with the new view whenever a filter changes.
        """
        self._listeners.append(listener)

    def show(self) -> None:
        grid = widgets.GridBox(self._widgets, layout=widgets.Layout(grid_template_columns="repeat(3, 1fr)",
                                                                    grid_gap="8px 24px"))
        display(widgets.VBox([widgets.HTML("<h3 style='margin:0 0 8px 0'>Dashboard filters</h3>"), grid],
                             layout=widgets.Layout(border="1px solid #d0d7de", padding="12px 16px")))

    def _changed(self, *_):
        self._view = None
        view = self.current_view()
        for listener in self._listeners:
            listener(view)
