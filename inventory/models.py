import datetime
from django.core.exceptions import ValidationError
from django.db import models, transaction


class Item(models.Model):
    class Category(models.TextChoices):
        FURNITURE = "FURNITURE", "Furniture"
        BOOKS = "BOOKS", "Books & Stationery"
        ELECTRONICS = "ELECTRONICS", "Electronics"
        KITCHEN = "KITCHEN", "Kitchen / Langar"
        CLEANING = "CLEANING", "Cleaning"
        PRAYER = "PRAYER", "Prayer / Masjid items"
        OTHER = "OTHER", "Other"

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=15, choices=Category.choices, default=Category.OTHER)
    quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=20, default="pcs")
    min_quantity = models.PositiveIntegerField(default=0, help_text="Show a low-stock warning at or below this amount")
    location = models.CharField(max_length=100, blank=True)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["name"]

    @property
    def is_low(self):
        return self.quantity <= self.min_quantity

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"


class StockMovement(models.Model):
    class Kind(models.TextChoices):
        IN = "IN", "Stock In (received / purchased)"
        OUT = "OUT", "Stock Out (used / issued)"

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="movements")
    kind = models.CharField(max_length=3, choices=Kind.choices)
    quantity = models.PositiveIntegerField()
    date = models.DateField(default=datetime.date.today)
    note = models.CharField(max_length=200, blank=True)
    by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-date", "-id"]

    def clean(self):
        if self.quantity is not None and self.quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        if not self.pk and self.kind == self.Kind.OUT and self.item_id and self.quantity and self.quantity > self.item.quantity:
            raise ValidationError(f"Only {self.item.quantity} {self.item.unit} in stock.")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        with transaction.atomic():
            super().save(*args, **kwargs)
            if is_new:
                delta = self.quantity if self.kind == self.Kind.IN else -self.quantity
                Item.objects.filter(pk=self.item_id).update(quantity=models.F("quantity") + delta)

    def __str__(self):
        return f"{self.get_kind_display()} {self.quantity} × {self.item.name}"
