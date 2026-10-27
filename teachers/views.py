from accounts.mixins import RoleRequiredMixin, MANAGEMENT_ROLES, STAFF_ROLES
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView
from django.contrib.auth import get_user_model

from .models import Teacher
from .forms import TeacherForm, TeacherUserForm

User = get_user_model()


class TeacherListView(RoleRequiredMixin, ListView):
    model = Teacher
    template_name = "teachers/teacher_list.html"
    context_object_name = "teachers"
    paginate_by = 15
    allowed_roles = STAFF_ROLES

    def get_queryset(self):
        qs = Teacher.objects.select_related("user").all()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(user__first_name__icontains=q) | qs.filter(user__last_name__icontains=q) | qs.filter(employee_id__icontains=q)
        return qs


class TeacherDetailView(RoleRequiredMixin, DetailView):
    model = Teacher
    template_name = "teachers/teacher_detail.html"
    context_object_name = "teacher"
    allowed_roles = STAFF_ROLES


class TeacherDeleteView(RoleRequiredMixin, DeleteView):
    model = Teacher
    template_name = "teachers/teacher_confirm_delete.html"
    success_url = reverse_lazy("teachers:list")
    allowed_roles = MANAGEMENT_ROLES


from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required


@role_required(*MANAGEMENT_ROLES)
def teacher_create(request):
    if request.method == "POST":
        uform = TeacherUserForm(request.POST)
        tform = TeacherForm(request.POST)
        if uform.is_valid() and tform.is_valid():
            user = uform.save(commit=False)
            user.role = User.Role.TEACHER
            user.set_password("changeme123")
            user.save()
            teacher = tform.save(commit=False)
            teacher.user = user
            teacher.save()
            messages.success(request, "Teacher added successfully. Default password: changeme123")
            return redirect("teachers:list")
    else:
        uform = TeacherUserForm()
        tform = TeacherForm()
    return render(request, "teachers/teacher_form.html", {"uform": uform, "tform": tform})


@role_required(*MANAGEMENT_ROLES)
def teacher_edit(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == "POST":
        uform = TeacherUserForm(request.POST, instance=teacher.user)
        tform = TeacherForm(request.POST, instance=teacher)
        if uform.is_valid() and tform.is_valid():
            uform.save()
            tform.save()
            messages.success(request, "Teacher updated successfully.")
            return redirect("teachers:list")
    else:
        uform = TeacherUserForm(instance=teacher.user)
        tform = TeacherForm(instance=teacher)
    return render(request, "teachers/teacher_form.html", {"uform": uform, "tform": tform, "teacher": teacher})
