from django.urls import path
from . import views

app_name = "attendance"

urlpatterns = [
    path("mark/", views.MarkAttendanceView.as_view(), name="mark"),
    path("report/", views.AttendanceReportView.as_view(), name="report"),
]
