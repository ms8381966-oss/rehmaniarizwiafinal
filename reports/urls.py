from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.ReportsIndexView.as_view(), name="index"),
    path("export/", views.ReportsExportView.as_view(), name="export"),
    path("whatsapp-report/generate/", views.GenerateWhatsAppReportView.as_view(), name="generate_whatsapp_report"),
]
