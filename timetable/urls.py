from django.urls import path
from . import views

app_name = "timetable"

urlpatterns = [
    path("", views.timetable_view, name="view"),
    path("mine/", views.my_schedule, name="mine"),
    path("add/", views.PeriodCreateView.as_view(), name="add"),
    path("<int:pk>/edit/", views.PeriodUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.PeriodDeleteView.as_view(), name="delete"),
]
