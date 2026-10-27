import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class HifzRecord(models.Model):
    """Daily Quran progress: Sabaq (new lesson), Sabqi (recent revision) and Manzil (old revision)."""

    class Kind(models.TextChoices):
        SABAQ = "SABAQ", "Sabaq (new lesson)"
        SABQI = "SABQI", "Sabqi (recent revision)"
        MANZIL = "MANZIL", "Manzil (old revision)"

    class Performance(models.TextChoices):
        EXCELLENT = "EXCELLENT", "Excellent"
        GOOD = "GOOD", "Good"
        AVERAGE = "AVERAGE", "Average"
        WEAK = "WEAK", "Weak"

    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="hifz_records")
    date = models.DateField(default=datetime.date.today)
    kind = models.CharField(max_length=7, choices=Kind.choices, default=Kind.SABAQ)
    para = models.PositiveSmallIntegerField("Para (Juz)", validators=[MinValueValidator(1), MaxValueValidator(30)])
    portion = models.CharField(max_length=100, blank=True, help_text="e.g. Page 3–5, Ruku 2, Surah name")
    performance = models.CharField(max_length=10, choices=Performance.choices, default=Performance.GOOD)
    remarks = models.CharField(max_length=200, blank=True)
    recorded_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.student} — {self.get_kind_display()} Para {self.para} ({self.date})"
