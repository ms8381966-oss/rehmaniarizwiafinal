from accounts.mixins import RoleRequiredMixin, MANAGEMENT_ROLES, STAFF_ROLES
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import SchoolClass, Section, Subject, AcademicYear
from .forms import SchoolClassForm, SectionForm, SubjectForm, AcademicYearForm


class ClassListView(RoleRequiredMixin, ListView):
    model = SchoolClass
    template_name = "academics/class_list.html"
    context_object_name = "classes"
    allowed_roles = STAFF_ROLES


class ClassCreateView(RoleRequiredMixin, CreateView):
    model = SchoolClass
    form_class = SchoolClassForm
    template_name = "academics/generic_form.html"
    success_url = reverse_lazy("academics:class_list")
    extra_context = {"title": "Add Class"}
    allowed_roles = MANAGEMENT_ROLES


class ClassUpdateView(RoleRequiredMixin, UpdateView):
    model = SchoolClass
    form_class = SchoolClassForm
    template_name = "academics/generic_form.html"
    success_url = reverse_lazy("academics:class_list")
    extra_context = {"title": "Edit Class"}
    allowed_roles = MANAGEMENT_ROLES


class ClassDeleteView(RoleRequiredMixin, DeleteView):
    model = SchoolClass
    template_name = "academics/generic_confirm_delete.html"
    success_url = reverse_lazy("academics:class_list")
    allowed_roles = MANAGEMENT_ROLES


class SectionListView(RoleRequiredMixin, ListView):
    model = Section
    template_name = "academics/section_list.html"
    context_object_name = "sections"
    allowed_roles = STAFF_ROLES


class SectionCreateView(RoleRequiredMixin, CreateView):
    model = Section
    form_class = SectionForm
    template_name = "academics/generic_form.html"
    success_url = reverse_lazy("academics:section_list")
    extra_context = {"title": "Add Section"}
    allowed_roles = MANAGEMENT_ROLES


class SectionUpdateView(RoleRequiredMixin, UpdateView):
    model = Section
    form_class = SectionForm
    template_name = "academics/generic_form.html"
    success_url = reverse_lazy("academics:section_list")
    extra_context = {"title": "Edit Section"}
    allowed_roles = MANAGEMENT_ROLES


class SectionDeleteView(RoleRequiredMixin, DeleteView):
    model = Section
    template_name = "academics/generic_confirm_delete.html"
    success_url = reverse_lazy("academics:section_list")
    allowed_roles = MANAGEMENT_ROLES


class SubjectListView(RoleRequiredMixin, ListView):
    model = Subject
    template_name = "academics/subject_list.html"
    context_object_name = "subjects"
    allowed_roles = STAFF_ROLES


class SubjectCreateView(RoleRequiredMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = "academics/generic_form.html"
    success_url = reverse_lazy("academics:subject_list")
    extra_context = {"title": "Add Subject"}
    allowed_roles = MANAGEMENT_ROLES


class SubjectUpdateView(RoleRequiredMixin, UpdateView):
    model = Subject
    form_class = SubjectForm
    template_name = "academics/generic_form.html"
    success_url = reverse_lazy("academics:subject_list")
    extra_context = {"title": "Edit Subject"}
    allowed_roles = MANAGEMENT_ROLES


class SubjectDeleteView(RoleRequiredMixin, DeleteView):
    model = Subject
    template_name = "academics/generic_confirm_delete.html"
    success_url = reverse_lazy("academics:subject_list")
    allowed_roles = MANAGEMENT_ROLES


class AcademicYearListView(RoleRequiredMixin, ListView):
    model = AcademicYear
    template_name = "academics/year_list.html"
    context_object_name = "years"
    allowed_roles = STAFF_ROLES


class AcademicYearCreateView(RoleRequiredMixin, CreateView):
    model = AcademicYear
    form_class = AcademicYearForm
    template_name = "academics/generic_form.html"
    success_url = reverse_lazy("academics:year_list")
    extra_context = {"title": "Add Academic Year"}
    allowed_roles = MANAGEMENT_ROLES
