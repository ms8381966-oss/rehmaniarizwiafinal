from django.urls import path
from . import views

app_name = "academics"

urlpatterns = [
    path("years/", views.AcademicYearListView.as_view(), name="year_list"),
    path("years/add/", views.AcademicYearCreateView.as_view(), name="year_add"),

    path("classes/", views.ClassListView.as_view(), name="class_list"),
    path("classes/add/", views.ClassCreateView.as_view(), name="class_add"),
    path("classes/<int:pk>/edit/", views.ClassUpdateView.as_view(), name="class_edit"),
    path("classes/<int:pk>/delete/", views.ClassDeleteView.as_view(), name="class_delete"),

    path("sections/", views.SectionListView.as_view(), name="section_list"),
    path("sections/add/", views.SectionCreateView.as_view(), name="section_add"),
    path("sections/<int:pk>/edit/", views.SectionUpdateView.as_view(), name="section_edit"),
    path("sections/<int:pk>/delete/", views.SectionDeleteView.as_view(), name="section_delete"),

    path("subjects/", views.SubjectListView.as_view(), name="subject_list"),
    path("subjects/add/", views.SubjectCreateView.as_view(), name="subject_add"),
    path("subjects/<int:pk>/edit/", views.SubjectUpdateView.as_view(), name="subject_edit"),
    path("subjects/<int:pk>/delete/", views.SubjectDeleteView.as_view(), name="subject_delete"),
]
