from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import role_required
from accounts.mixins import TEACHING_ROLES
from accounts.utils import allowed_sections, allowed_students, family_students, is_management
from students.models import Student

from .forms import HifzForm
from .models import HifzRecord
from .services import progress_summary


@role_required(*TEACHING_ROLES)
def record_list(request):
    qs = HifzRecord.objects.filter(student__in=allowed_students(request.user, strict=True)).select_related("student", "student__section")
    section = request.GET.get("section")
    kind = request.GET.get("kind")
    date = request.GET.get("date")
    if section:
        qs = qs.filter(student__section_id=section)
    if kind:
        qs = qs.filter(kind=kind)
    if date:
        qs = qs.filter(date=date)
    return render(request, "hifz/record_list.html", {
        "records": qs[:200], "sections": allowed_sections(request.user, strict=True), "kinds": HifzRecord.Kind.choices,
        "f_section": section or "", "f_kind": kind or "", "f_date": date or "",
    })


@role_required(*TEACHING_ROLES)
def record_add(request):
    initial = {}
    if request.GET.get("student"):
        initial["student"] = request.GET["student"]
    form = HifzForm(request.POST or None, user=request.user, initial=initial)
    if request.method == "POST" and form.is_valid():
        rec = form.save(commit=False)
        rec.recorded_by = request.user
        rec.save()
        messages.success(request, "Quran progress recorded.")
        return redirect("hifz:list")
    return render(request, "partials/form.html", {"form": form, "title": "Record Quran Progress"})


@role_required(*TEACHING_ROLES)
def record_delete(request, pk):
    rec = get_object_or_404(HifzRecord, pk=pk, student__in=allowed_students(request.user, strict=True))
    if request.method == "POST":
        rec.delete()
        messages.success(request, "Record deleted.")
        return redirect("hifz:list")
    return render(request, "partials/confirm_delete.html", {"object": rec})


@login_required
def student_progress(request, pk):
    student = get_object_or_404(Student, pk=pk)
    user = request.user
    if user.role in ("STUDENT", "PARENT") and not user.is_superuser:
        if not family_students(user).filter(pk=student.pk).exists():
            raise PermissionDenied
    elif not allowed_students(user, strict=True).filter(pk=student.pk).exists():
        raise PermissionDenied
    return render(request, "hifz/student_progress.html", {
        "student": student, "summary": progress_summary(student),
        "records": student.hifz_records.all()[:100],
        "can_add": is_management(user) or user.role == "TEACHER",
    })
