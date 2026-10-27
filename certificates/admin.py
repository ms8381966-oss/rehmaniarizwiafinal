from django.contrib import admin
from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("serial", "student", "kind", "issue_date")
    list_filter = ("kind",)
    readonly_fields = ("serial",)
