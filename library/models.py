from decimal import Decimal
from django.db import models


class Book(models.Model):
    SALE_CHOICES = [
        ('FOR_SALE', 'For Sale'),
        ('NOT_FOR_SALE', 'Not For Sale'),
    ]
    
    PUBLICATION_CHOICES = [
        ('OWN', 'Own Publication'),
        ('NORMAL', 'Normal Book'),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150, blank=True)
    category = models.CharField(max_length=100, blank=True, help_text="e.g. Tafseer, Hadith, Fiqh, Seerah, Urdu, English")
    language = models.CharField(max_length=50, blank=True, help_text="e.g. Arabic, Urdu, English")
    isbn = models.CharField("ISBN / Book No.", max_length=30, blank=True)
    copies = models.PositiveIntegerField(default=1)
    shelf = models.CharField(max_length=30, blank=True)
    
    sale_status = models.CharField(
        max_length=20, 
        choices=SALE_CHOICES, 
        default='NOT_FOR_SALE',
        verbose_name="Sale Status"
    )
    publication_type = models.CharField(
        max_length=20, 
        choices=PUBLICATION_CHOICES, 
        default='NORMAL',
        verbose_name="Publication Type"
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal("0.00"), 
        help_text="Price if for sale"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.get_publication_type_display()})"


class Sale(models.Model):
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="library_sales")
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the exact time of transaction
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    sold_at = models.DateTimeField(auto_now_add=True)
    sold_to = models.CharField(max_length=255, null=True, blank=True)   # Optional Customer Tracking Field

    class Meta:
        ordering = ["-sold_at"]

    def __str__(self):
        return f"Sale: {self.book.title} x {self.quantity} to {self.sold_to or 'Walk-in Customer'}"
