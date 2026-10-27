from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.ItemListView.as_view(), name="list"),
    path("add/", views.ItemCreateView.as_view(), name="add"),
    path("<int:pk>/edit/", views.ItemUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.ItemDeleteView.as_view(), name="delete"),
    path("movements/", views.MovementListView.as_view(), name="movements"),
    path("movements/add/", views.MovementCreateView.as_view(), name="movement_add"),
]
