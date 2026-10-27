from django.urls import path
from . import views

app_name = "portal"

urlpatterns = [
    path("", views.my_portal, name="home"),
    path("child/<int:pk>/", views.child_detail, name="child_detail"),
]
