from django.contrib import admin
from .models import Exam, ExamResult


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("name", "school_class", "start_date", "is_published")
    list_filter = ("is_published", "school_class")


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ("exam", "student", "subject", "obtained_marks", "total_marks")
    list_filter = ("exam", "subject")
    search_fields = ("student__first_name", "student__last_name", "student__admission_number")
