from django.urls import path
from . import views

app_name = "exams"

urlpatterns = [
    path("", views.ExamListView.as_view(), name="list"),
    path("add/", views.ExamCreateView.as_view(), name="add"),
    path("<int:pk>/", views.exam_detail, name="detail"),
    path("<int:pk>/edit/", views.ExamUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.ExamDeleteView.as_view(), name="delete"),
    path("<int:pk>/marks/", views.marks_entry, name="marks"),
    path("<int:exam_pk>/report-card/<int:student_pk>/", views.report_card, name="report_card"),
]
