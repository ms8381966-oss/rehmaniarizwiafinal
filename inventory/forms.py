import datetime
from accounts.widgets import BootstrapModelForm
from .models import Item, StockMovement


class ItemForm(BootstrapModelForm):
    class Meta:
        model = Item
        fields = ["name", "category", "quantity", "unit", "min_quantity", "location", "notes"]


class MovementForm(BootstrapModelForm):
    class Meta:
        model = StockMovement
        fields = ["item", "kind", "quantity", "date", "note"]
