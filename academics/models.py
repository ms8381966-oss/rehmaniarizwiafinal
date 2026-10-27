from django.db import models


class AcademicYear(models.Model):
    name = models.CharField(max_length=20, unique=True)  # e.g. 2025-2026
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class SchoolClass(models.Model):
    name = models.CharField(max_length=50)  # e.g. Grade 1
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="classes")

    class Meta:
        unique_together = ["name", "academic_year"]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.academic_year})"


class Section(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="sections")
    name = models.CharField(max_length=10)  # e.g. A, B
    class_teacher = models.ForeignKey("teachers.Teacher", on_delete=models.SET_NULL, null=True, blank=True, related_name="class_sections")
    room_number = models.CharField(max_length=20, blank=True)

    class Meta:
        unique_together = ["school_class", "name"]
        ordering = ["school_class", "name"]

    def __str__(self):
        return f"{self.school_class.name} - {self.name}"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="subjects")
    teacher = models.ForeignKey("teachers.Teacher", on_delete=models.SET_NULL, null=True, blank=True, related_name="subjects")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"
