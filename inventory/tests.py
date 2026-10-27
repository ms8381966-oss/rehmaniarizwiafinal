from django.test import TestCase
from django.core.exceptions import ValidationError

from .models import Item, StockMovement


class InventoryTests(TestCase):
    def test_stock_in_out_updates_quantity(self):
        item = Item.objects.create(name="Markers", quantity=5, min_quantity=3)
        StockMovement.objects.create(item=item, kind="IN", quantity=10)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 15)
        StockMovement.objects.create(item=item, kind="OUT", quantity=13)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)
        self.assertTrue(item.is_low)

    def test_cannot_take_out_more_than_stock(self):
        item = Item.objects.create(name="Mats", quantity=2)
        with self.assertRaises(ValidationError):
            StockMovement(item=item, kind="OUT", quantity=5).full_clean()
