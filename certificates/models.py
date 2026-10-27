import datetime
from django.db import models


class Certificate(models.Model):
    class Kind(models.TextChoices):
        CHARACTER = "CHARACTER", "Character Certificate"
        LEAVING = "LEAVING", "Leaving Certificate"
        HIFZ = "HIFZ", "Hifz-e-Quran Completion"
        NAZRA = "NAZRA", "Nazra Quran Completion"
        MERIT = "MERIT", "Merit / Appreciation"

    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="certificates")
    kind = models.CharField(max_length=12, choices=Kind.choices)
    serial = models.CharField(max_length=30, unique=True, blank=True, editable=False)
    issue_date = models.DateField(default=datetime.date.today)
    details = models.TextField(blank=True, help_text="Optional extra line printed on the certificate (e.g. grade, position, reason for leaving)")
    issued_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-issue_date", "-id"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.serial:
            self.serial = f"JRR-{self.issue_date.year}-{self.pk:04d}"
            super().save(update_fields=["serial"])

    def __str__(self):
        return f"{self.get_kind_display()} — {self.student} ({self.serial})"
