import datetime
from django.db import models


class Homework(models.Model):
    section = models.ForeignKey("academics.Section", on_delete=models.CASCADE, related_name="homework")
    subject = models.ForeignKey("academics.Subject", on_delete=models.SET_NULL, null=True, blank=True, related_name="homework")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_on = models.DateField(default=datetime.date.today)
    due_date = models.DateField()
    attachment = models.FileField(upload_to="homework/", blank=True, null=True)
    assigned_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-due_date", "-id"]
        verbose_name_plural = "Homework"

    def __str__(self):
        return f"{self.title} ({self.section})"
