from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from accounts.decorators import role_required
from accounts.mixins import TEACHING_ROLES
from accounts.utils import allowed_sections, family_students, is_management

from .forms import HomeworkForm
from .models import Homework


@login_required
def homework_list(request):
    user = request.user
    qs = Homework.objects.select_related("section__school_class", "subject", "assigned_by")
    if user.is_superuser or user.role in ("SUPER_ADMIN", "PRINCIPAL", "ADMIN"):
        pass
    elif user.role == "TEACHER":
        qs = qs.filter(section__in=allowed_sections(user))
    elif user.role in ("STUDENT", "PARENT"):
        qs = qs.filter(section__students__in=family_students(user)).distinct()
    else:
        raise PermissionDenied
    can_edit = is_management(user) or user.role == "TEACHER"
    return render(request, "homework/homework_list.html", {"items": qs[:100], "can_edit": can_edit})


def _editable(user, hw):
    return is_management(user) or (user.role == "TEACHER" and allowed_sections(user).filter(pk=hw.section_id).exists())


@role_required(*TEACHING_ROLES)
def homework_add(request):
    form = HomeworkForm(request.POST or None, request.FILES or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        hw = form.save(commit=False)
        hw.assigned_by = request.user
        hw.save()
        messages.success(request, "Homework assigned.")
        return redirect("homework:list")
    return render(request, "partials/form.html", {"form": form, "title": "Assign Homework"})


@role_required(*TEACHING_ROLES)
def homework_edit(request, pk):
    hw = get_object_or_404(Homework, pk=pk)
    if not _editable(request.user, hw):
        raise PermissionDenied
    form = HomeworkForm(request.POST or None, request.FILES or None, instance=hw, user=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Homework updated.")
        return redirect("homework:list")
    return render(request, "partials/form.html", {"form": form, "title": "Edit Homework"})


@role_required(*TEACHING_ROLES)
def homework_delete(request, pk):
    hw = get_object_or_404(Homework, pk=pk)
    if not _editable(request.user, hw):
        raise PermissionDenied
    if request.method == "POST":
        hw.delete()
        messages.success(request, "Homework deleted.")
        return redirect("homework:list")
    return render(request, "partials/confirm_delete.html", {"object": hw})
