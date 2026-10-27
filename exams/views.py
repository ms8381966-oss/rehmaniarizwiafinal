from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from accounts.decorators import role_required
from accounts.mixins import RoleRequiredMixin, MANAGEMENT_ROLES, TEACHING_ROLES
from accounts.utils import allowed_sections, allowed_subjects, family_students, is_management
from students.models import Student

from .forms import ExamForm
from .models import Exam, ExamResult
from .services import student_summary, class_ranking


class ExamListView(RoleRequiredMixin, ListView):
    model = Exam
    template_name = "exams/exam_list.html"
    context_object_name = "exams"
    paginate_by = 20
    allowed_roles = TEACHING_ROLES

    def get_queryset(self):
        qs = Exam.objects.select_related("school_class")
        if not is_management(self.request.user):
            qs = qs.filter(school_class__sections__in=allowed_sections(self.request.user)).distinct()
        return qs


class ExamCreateView(RoleRequiredMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = "partials/form.html"
    success_url = reverse_lazy("exams:list")
    extra_context = {"title": "Add Exam"}
    allowed_roles = MANAGEMENT_ROLES


class ExamUpdateView(RoleRequiredMixin, UpdateView):
    model = Exam
    form_class = ExamForm
    template_name = "partials/form.html"
    success_url = reverse_lazy("exams:list")
    extra_context = {"title": "Edit Exam"}
    allowed_roles = MANAGEMENT_ROLES


class ExamDeleteView(RoleRequiredMixin, DeleteView):
    model = Exam
    template_name = "partials/confirm_delete.html"
    success_url = reverse_lazy("exams:list")
    allowed_roles = MANAGEMENT_ROLES


@role_required(*TEACHING_ROLES)
def marks_entry(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    sections = allowed_sections(request.user).filter(school_class=exam.school_class)
    subjects = allowed_subjects(request.user, exam.school_class)

    section = subject = None
    if request.GET.get("section"):
        section = get_object_or_404(sections, pk=request.GET["section"])
    if request.GET.get("subject"):
        subject = get_object_or_404(subjects, pk=request.GET["subject"])

    students = existing = None
    default_total = 100
    if section and subject:
        students = list(Student.objects.filter(section=section, status="ACTIVE").order_by("roll_number", "first_name"))
        existing = {r.student_id: r for r in ExamResult.objects.filter(exam=exam, subject=subject, student__in=students)}
        if existing:
            default_total = next(iter(existing.values())).total_marks

        if request.method == "POST":
            try:
                total = int(request.POST.get("total_marks") or 100)
                if total <= 0:
                    raise ValueError
            except ValueError:
                messages.error(request, "Total marks must be a positive number.")
                return redirect(request.get_full_path())
            saved, errors = 0, []
            for st in students:
                raw = (request.POST.get(f"marks_{st.pk}") or "").strip()
                if raw == "":
                    continue
                try:
                    obtained = Decimal(raw)
                except InvalidOperation:
                    errors.append(f"{st.full_name}: '{raw}' is not a number")
                    continue
                if obtained < 0 or obtained > total:
                    errors.append(f"{st.full_name}: marks must be between 0 and {total}")
                    continue
                ExamResult.objects.update_or_create(
                    exam=exam, student=st, subject=subject,
                    defaults={"total_marks": total, "obtained_marks": obtained, "entered_by": request.user},
                )
                saved += 1
            if saved:
                messages.success(request, f"Saved marks for {saved} student(s).")
            for e in errors:
                messages.error(request, e)
            return redirect(request.get_full_path())

    return render(request, "exams/marks_entry.html", {
        "exam": exam, "sections": sections, "subjects": subjects, "section": section, "subject": subject,
        "students": students, "default_total": default_total,
        "rows": [(st, (existing or {}).get(st.pk)) for st in (students or [])],
    })


@role_required(*TEACHING_ROLES)
def exam_detail(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    students = Student.objects.filter(section__school_class=exam.school_class, section__in=allowed_sections(request.user)).select_related("section")
    results = ExamResult.objects.filter(exam=exam, student__in=students).select_related("subject")
    subjects = sorted({r.subject for r in results}, key=lambda s: s.name)
    by_student = {}
    for r in results:
        by_student.setdefault(r.student_id, {})[r.subject_id] = r
    ranking = class_ranking(exam)
    rows = []
    for st in students:
        cells = by_student.get(st.pk, {})
        if not cells:
            continue
        _, totals = student_summary(exam, st)
        rows.append({
            "student": st, "cells": [cells.get(s.pk) for s in subjects], "totals": totals,
            "position": ranking.get(st.pk, ("-", None))[0],
        })
    rows.sort(key=lambda r: (r["position"] if isinstance(r["position"], int) else 9999))
    return render(request, "exams/exam_detail.html", {"exam": exam, "subjects": subjects, "rows": rows})


def _can_view_student(user, student):
    if is_management(user):
        return True
    if user.role == "TEACHER":
        return allowed_sections(user).filter(pk=student.section_id).exists()
    return family_students(user).filter(pk=student.pk).exists()


def report_card(request, exam_pk, student_pk):
    if not request.user.is_authenticated:
        raise PermissionDenied
    exam = get_object_or_404(Exam, pk=exam_pk)
    student = get_object_or_404(Student, pk=student_pk)
    if not _can_view_student(request.user, student):
        raise PermissionDenied
    if request.user.role in ("STUDENT", "PARENT") and not request.user.is_superuser and not exam.is_published:
        raise PermissionDenied("This result has not been published yet.")
    results, totals = student_summary(exam, student)
    ranking = class_ranking(exam)
    position, _ = ranking.get(student.pk, (None, None))
    return render(request, "exams/report_card.html", {
        "exam": exam, "student": student, "results": results, "totals": totals,
        "position": position, "class_size": len(ranking),
    })
