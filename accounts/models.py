from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
        PRINCIPAL = "PRINCIPAL", "Principal"
        ADMIN = "ADMIN", "Admin"
        TEACHER = "TEACHER", "Teacher"
        STUDENT = "STUDENT", "Student"
        PARENT = "PARENT", "Parent"
        ACCOUNTANT = "ACCOUNTANT", "Accountant"
        LIBRARIAN = "LIBRARIAN", "Librarian"
        STAFF = "STAFF", "Staff"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)

    def is_role(self, role):
        return self.role == role

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
