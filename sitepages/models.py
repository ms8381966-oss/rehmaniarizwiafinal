from django.db import models


class SiteSettings(models.Model):
    """Singleton-style settings for the public site — contact info, socials, and bank details
    for donations. Edit from the Django Admin panel (Sitepages > Site settings)."""
    phone = models.CharField(max_length=50, default="+92 344 5681779")
    email = models.EmailField(default="mssialvi721@gmail.com")
    address = models.CharField(max_length=255, default="Near Jamia Masjid Gulzar-e-Rehmat, close to the main Sohawa Bus Stop, G.T. Road, Sohawa, Jhelum")
    facebook_url = models.URLField(blank=True, help_text="Full URL to the school's Facebook page")
    whatsapp_number = models.CharField(max_length=50, blank=True, help_text="Digits with country code, e.g. 923445681779")
    website_url = models.URLField(blank=True, help_text="Existing public website (e.g. the Weebly page)")
    established_year = models.PositiveIntegerField(default=1988)
    founder_name = models.CharField(max_length=150, default="Hazrat Allama Qari Abdullah Sialvi")

    bank_name = models.CharField(max_length=150, blank=True)
    account_title = models.CharField(max_length=150, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    iban = models.CharField(max_length=50, blank=True)
    branch_code = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    @classmethod
    def get_solo(cls):
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create()
        return obj


class ContactMessage(models.Model):
    """Messages sent through the public Contact form (read them in Admin > Contact messages)."""
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return f"{self.name} - {self.subject or 'No subject'}"
