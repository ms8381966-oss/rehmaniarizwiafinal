from django.core.exceptions import ValidationError
from django.db import models


class Period(models.Model):
    class Day(models.IntegerChoices):
        MON = 0, "Monday"
        TUE = 1, "Tuesday"
        WED = 2, "Wednesday"
        THU = 3, "Thursday"
        FRI = 4, "Friday"
        SAT = 5, "Saturday"
        SUN = 6, "Sunday"

    section = models.ForeignKey("academics.Section", on_delete=models.CASCADE, related_name="periods")
    day = models.PositiveSmallIntegerField(choices=Day.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject = models.ForeignKey("academics.Subject", on_delete=models.SET_NULL, null=True, blank=True, related_name="periods")
    teacher = models.ForeignKey("teachers.Teacher", on_delete=models.SET_NULL, null=True, blank=True, related_name="periods")
    room = models.CharField(max_length=30, blank=True)

    class Meta:
        unique_together = ["section", "day", "start_time"]
        ordering = ["day", "start_time"]

    def clean(self):
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")
        if self.subject_id and self.section_id and self.subject.school_class_id != self.section.school_class_id:
            raise ValidationError("This subject does not belong to the section's class.")
        if self.teacher_id and self.day is not None and self.start_time and self.end_time:
            clash = Period.objects.filter(
                teacher=self.teacher, day=self.day, start_time__lt=self.end_time, end_time__gt=self.start_time,
            ).exclude(pk=self.pk).exclude(section=self.section).first()
            if clash:
                raise ValidationError(f"{self.teacher} is already teaching {clash.section} at that time.")

    def __str__(self):
        return f"{self.section} {self.get_day_display()} {self.start_time:%H:%M}"
