from django.urls import path
from . import views

app_name = "homework"

urlpatterns = [
    path("", views.homework_list, name="list"),
    path("add/", views.homework_add, name="add"),
    path("<int:pk>/edit/", views.homework_edit, name="edit"),
    path("<int:pk>/delete/", views.homework_delete, name="delete"),
]
