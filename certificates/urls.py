from django.urls import path
from . import views

app_name = "certificates"

urlpatterns = [
    path("", views.CertificateListView.as_view(), name="list"),
    path("issue/", views.CertificateCreateView.as_view(), name="add"),
    path("<int:pk>/print/", views.certificate_print, name="print"),
    path("<int:pk>/delete/", views.CertificateDeleteView.as_view(), name="delete"),
]
