from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "publication_type", "sale_status", "price", "copies", "shelf")
    list_filter = ("publication_type", "sale_status", "category")
    search_fields = ("title", "author", "isbn")