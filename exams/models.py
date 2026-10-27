from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models

PASS_PERCENT = Decimal("40")


def grade_for(percentage):
    p = Decimal(percentage)
    if p >= 90: return "A+"
    if p >= 80: return "A"
    if p >= 70: return "B"
    if p >= 60: return "C"
    if p >= 50: return "D"
    if p >= PASS_PERCENT: return "E"
    return "F"


class Exam(models.Model):
    name = models.CharField(max_length=150, help_text="e.g. Mid-Term 2026, Annual Exam, Monthly Test")
    school_class = models.ForeignKey("academics.SchoolClass", on_delete=models.CASCADE, related_name="exams")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_published = models.BooleanField(default=False, help_text="Tick to let students and parents see the result cards")

    class Meta:
        ordering = ["-start_date", "name"]

    def __str__(self):
        return f"{self.name} — {self.school_class.name}"


class ExamResult(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="results")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="exam_results")
    subject = models.ForeignKey("academics.Subject", on_delete=models.CASCADE, related_name="exam_results")
    total_marks = models.PositiveSmallIntegerField(default=100)
    obtained_marks = models.DecimalField(max_digits=6, decimal_places=2)
    remarks = models.CharField(max_length=200, blank=True)
    entered_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ["exam", "student", "subject"]
        ordering = ["subject__name"]

    def clean(self):
        if self.obtained_marks is not None and self.obtained_marks > self.total_marks:
            raise ValidationError("Obtained marks cannot exceed total marks.")
        if self.obtained_marks is not None and self.obtained_marks < 0:
            raise ValidationError("Obtained marks cannot be negative.")

    @property
    def percentage(self):
        if not self.total_marks:
            return Decimal("0")
        return (self.obtained_marks / self.total_marks * 100).quantize(Decimal("0.1"))

    @property
    def grade(self):
        return grade_for(self.percentage)

    @property
    def passed(self):
        return self.percentage >= PASS_PERCENT

    def __str__(self):
        return f"{self.student} {self.subject} {self.obtained_marks}/{self.total_marks}"
