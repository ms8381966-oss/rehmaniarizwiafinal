from django.urls import path
from . import views

app_name = "notices"

urlpatterns = [
    path("", views.NoticeListView.as_view(), name="list"),
    path("add/", views.NoticeCreateView.as_view(), name="add"),
    path("<int:pk>/edit/", views.NoticeUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.NoticeDeleteView.as_view(), name="delete"),

    path("events/", views.EventListView.as_view(), name="event_list"),
    path("events/add/", views.EventCreateView.as_view(), name="event_add"),
]
