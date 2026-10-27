from django.contrib import admin
from .models import HifzRecord


@admin.register(HifzRecord)
class HifzAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "kind", "para", "performance")
    list_filter = ("kind", "performance")
