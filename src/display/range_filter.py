import ipywidgets as widgets
import pandas as pd

from .filter import Filter


class RangeFilter(Filter):
    """A slider keeping rows whose number lies between the two handles."""

    def __init__(self, column: str, label: str, step: int = 1, width: str = "100%"):
        super().__init__(column, label, width)
        self.step = step

    def _make_widget(self, values):
        numbers = pd.to_numeric(values, errors="raise")
        low, high = int(numbers.min()), int(numbers.max())
        return widgets.IntRangeSlider(description=self.label, min=low, max=high,
                                      value=(low, high), step=self.step)

    def mask(self, frame):
        low, high = self.widget.value
        return pd.to_numeric(frame[self.column]).between(low, high)

    def reset(self):
        self.widget.value = (self.widget.min, self.widget.max)