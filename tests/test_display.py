from types import SimpleNamespace

import pandas as pd
import pytest

from src.display import ChoiceFilter, DashboardList, Display, DisplayError, RangeFilter, TextFilter


class FruitList(Display):
    title = "Fruit"
    columns = ["name", "colour", "price"]
    sort_by = ["price"]

    def __init__(self, frame, filters=None, **options):
        self._rows = frame
        self._filters = filters
        super().__init__(**options)

    def build_frame(self):
        return self._rows

    def build_filters(self):
        if self._filters is not None:
            return self._filters
        return [TextFilter("name", "Name"), ChoiceFilter("colour", "Colour"), RangeFilter("price", "Price")]


FRUIT = pd.DataFrame({"name": ["Apple", "Banana", "Cherry", "Date", "Elderberry"],
                      "colour": ["red", "yellow", "red", "brown", "black"],
                      "price": [300, 100, 5000, 2500, 1200]})


def test_matches_are_sorted_numbered_from_one_and_paged():
    fruit = FruitList(FRUIT, page_size=2)

    assert fruit.matches()["name"].tolist() == ["Banana", "Apple", "Elderberry", "Date", "Cherry"]
    assert fruit.matches().index.tolist() == [1, 2, 3, 4, 5]
    assert fruit.page_count() == 3
    fruit.go_to_page(99)
    assert fruit.page == 3 and fruit.current_page()["name"].tolist() == ["Cherry"]
    fruit.go_to_page(-5)
    assert fruit.page == 1


def test_filters_combine_and_reset():
    fruit = FruitList(FRUIT)
    fruit.widget()
    name, colour, price = fruit.filters

    colour.widget.value = "red"
    assert fruit.matches()["name"].tolist() == ["Apple", "Cherry"]
    price.widget.value = (0, 1000)
    assert fruit.matches()["name"].tolist() == ["Apple"]
    name.widget.value = "ban"
    assert fruit.matches().empty
    assert fruit._count.value.startswith("<b>0</b> of 5")

    fruit._reset(None)
    assert len(fruit.matches()) == 5


def test_text_filter_ignores_case_and_trims_to_max_length():
    text = TextFilter("name", "Name", max_length=3)
    fruit = FruitList(FRUIT, filters=[text])
    text.widget.value = "ELDERS"
    assert text.widget.value == "ELD"
    assert fruit.matches()["name"].tolist() == ["Elderberry"]


def test_choice_filter_offers_all_plus_each_value():
    choice = ChoiceFilter("colour", "Colour")
    FruitList(FRUIT, filters=[choice])
    assert choice.widget.options == ("All", "black", "brown", "red", "yellow")


def test_unknown_columns_and_bad_options_are_errors():
    with pytest.raises(DisplayError, match="unknown columns: price"):
        FruitList(FRUIT.drop(columns="price"), filters=[])
    with pytest.raises(DisplayError, match="unknown column 'weight'"):
        FruitList(FRUIT, filters=[TextFilter("weight", "Weight")])
    with pytest.raises(DisplayError, match="page_size must be at least 1"):
        FruitList(FRUIT, page_size=0)
    with pytest.raises(DisplayError, match="filter_cols_per_row must be at least 1"):
        FruitList(FRUIT, filter_cols_per_row=0)


def test_widget_shows_the_title_and_the_first_page():
    fruit = FruitList(FRUIT, page_size=2)
    box = fruit.widget()
    assert "Fruit" in box.children[0].children[1].value
    assert "Banana" in fruit._table.value and "Cherry" not in fruit._table.value


class PriceList(DashboardList):
    title = "Prices"
    columns = ["name", "price"]
    sort_by = ["price"]

    def table(self, view):
        return view.prices


def test_dashboard_list_follows_new_views_and_groups_thousands():
    prices = PriceList(SimpleNamespace(prices=FRUIT), list_page_size=2)
    prices.widget()
    prices.go_to_page(2)
    assert "5,000" in prices._table.value or "2,500" in prices._table.value

    prices.update(SimpleNamespace(prices=FRUIT.head(1)))
    assert prices.page == 1 and prices.matches()["name"].tolist() == ["Apple"]
    with pytest.raises(DisplayError, match="unknown columns"):
        prices.update(SimpleNamespace(prices=FRUIT[["name"]]))
