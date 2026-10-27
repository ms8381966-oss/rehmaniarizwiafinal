from django.db import models


class Notice(models.Model):
    class Audience(models.TextChoices):
        ALL = "ALL", "Everyone"
        TEACHERS = "TEACHERS", "Teachers"
        STUDENTS = "STUDENTS", "Students"
        PARENTS = "PARENTS", "Parents"
        STAFF = "STAFF", "Staff"

    title = models.CharField(max_length=200)
    content = models.TextField()
    audience = models.CharField(max_length=10, choices=Audience.choices, default=Audience.ALL)
    published_on = models.DateTimeField(auto_now_add=True)
    published_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    is_pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_pinned", "-published_on"]

    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    location = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.title} ({self.date})"
