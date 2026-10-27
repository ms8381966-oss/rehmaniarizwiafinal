from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("sitepages.urls")),
    path("accounts/", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("portal/", include("portal.urls")),
    path("reports/", include("reports.urls")),
    path("students/", include("students.urls")),
    path("teachers/", include("teachers.urls")),
    path("academics/", include("academics.urls")),
    path("attendance/", include("attendance.urls")),
    path("fees/", include("fees.urls")),
    path("notices/", include("notices.urls")),
    path("exams/", include("exams.urls")),
    path("timetable/", include("timetable.urls")),
    path("homework/", include("homework.urls")),
    path("library/", include("library.urls")),
    path("inventory/", include("inventory.urls")),
    path("certificates/", include("certificates.urls")),
    path("hifz/", include("hifz.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
