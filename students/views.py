from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from accounts.mixins import RoleRequiredMixin, MANAGEMENT_ROLES, STAFF_ROLES
from .models import Student
from .forms import StudentForm
from academics.models import Section # <-- Yeh line top par lazmi add karein


class StudentListView(RoleRequiredMixin, ListView):
    """Admin/Principal see everyone. Teachers see only students in sections they teach."""
    model = Student
    template_name = "students/student_list.html"
    context_object_name = "students"
    paginate_by = 15
    allowed_roles = STAFF_ROLES

    def get_queryset(self):
        qs = Student.objects.select_related("section", "section__school_class").all()
        user = self.request.user
        
        # Role-based restriction for query logs
        if not user.is_superuser and user.role == "TEACHER":
            qs = qs.filter(section__class_teacher__user=user)
            
        q = self.request.GET.get("q")
        status = self.request.GET.get("status")
        section_id = self.request.GET.get("section") # <-- NEW: Fetch section parameter from URL

        if q:
            qs = qs.filter(
                Q(first_name__icontains=q) | Q(last_name__icontains=q) |
                Q(admission_number__icontains=q) | Q(roll_number__icontains=q)
            )
        if status:
            qs = qs.filter(status=status)
            
        # NEW: Section wise data filtering control
        if section_id:
            qs = qs.filter(section_id=section_id)
            
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        # Fetch sections list based on logged-in user role
        sections_qs = Section.objects.select_related('school_class').all()
        if not user.is_superuser and user.role == "TEACHER":
            sections_qs = sections_qs.filter(class_teacher__user=user)

        # Context updates mappings
        ctx["status_choices"] = Student.Status.choices
        ctx["sections_list"] = sections_qs # <-- NEW: Pass role-filtered sections to dropdown
        ctx["q"] = self.request.GET.get("q", "")
        ctx["status"] = self.request.GET.get("status", "")
        ctx["selected_section"] = self.request.GET.get("section", "") # <-- NEW: Keep filter selected on reload
        ctx["can_manage"] = self.request.user.is_superuser or self.request.user.role in MANAGEMENT_ROLES
        return ctx


class StudentDetailView(LoginRequiredMixin, DetailView):
    """Admin/teacher/principal can view any. A student/parent can only view their own / their child's."""
    model = Student
    template_name = "students/student_detail.html"
    context_object_name = "student"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if user.is_superuser or user.role in STAFF_ROLES:
            return obj
        if user.role == "STUDENT" and obj.user_id == user.id:
            return obj
        if user.role == "PARENT" and obj.parent_id == user.id:
            return obj
        raise PermissionDenied("You can only view your own record.")


class StudentCreateView(RoleRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = "students/student_form.html"
    success_url = reverse_lazy("students:list")
    allowed_roles = MANAGEMENT_ROLES

    def form_valid(self, form):
        messages.success(self.request, "Student registered successfully.")
        return super().form_valid(form)


class StudentUpdateView(RoleRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = "students/student_form.html"
    success_url = reverse_lazy("students:list")
    allowed_roles = MANAGEMENT_ROLES

    def form_valid(self, form):
        messages.success(self.request, "Student updated successfully.")
        return super().form_valid(form)


class StudentDeleteView(RoleRequiredMixin, DeleteView):
    model = Student
    template_name = "students/student_confirm_delete.html"
    success_url = reverse_lazy("students:list")
    allowed_roles = MANAGEMENT_ROLES

    def form_valid(self, form):
        messages.success(self.request, "Student deleted successfully.")
        return super().form_valid(form)
