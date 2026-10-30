import ipywidgets as widgets
import pandas as pd

from .filter import Filter


class ChoiceFilter(Filter):
    """A dropdown of the column's values, plus 'All'."""

    ALL = "All"

    def _make_widget(self, values):
        options = [self.ALL, *sorted(values.dropna().astype(str).unique())]
        return widgets.Dropdown(description=self.label, options=options)

    def mask(self, frame):
        if self.widget.value == self.ALL:
            return pd.Series(True, index=frame.index)
        return frame[self.column].astype(str) == self.widget.value

    def reset(self):
        self.widget.value = self.ALL
