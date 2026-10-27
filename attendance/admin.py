from django.contrib import admin
from .models import StudentAttendance, TeacherAttendance

admin.site.register(StudentAttendance)
admin.site.register(TeacherAttendance)
