from django.urls import path
from . import views

app_name = "hifz"

urlpatterns = [
    path("", views.record_list, name="list"),
    path("add/", views.record_add, name="add"),
    path("<int:pk>/delete/", views.record_delete, name="delete"),
    path("student/<int:pk>/", views.student_progress, name="student"),
]
