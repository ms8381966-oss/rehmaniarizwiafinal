from django.contrib import admin
from .models import SiteSettings, ContactMessage


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("About the Jamia", {"fields": ("established_year", "founder_name")}),
        ("Contact Info", {"fields": ("phone", "email", "address", "facebook_url", "whatsapp_number", "website_url")}),
        ("Bank Details (for donations)", {"fields": ("bank_name", "account_title", "account_number", "iban", "branch_code")}),
    )

    def has_add_permission(self, request):
        # Keep this a singleton — only allow adding if none exists yet
        return not SiteSettings.objects.exists()


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "email", "phone", "created_on", "is_read")
    list_filter = ("is_read",)
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_on",)
