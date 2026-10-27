import datetime
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from django.core.exceptions import PermissionDenied

from accounts.mixins import RoleRequiredMixin, MANAGEMENT_ROLES
from academics.models import Section
from students.models import Student
from .models import StudentAttendance


class MarkAttendanceView(RoleRequiredMixin, View):
    """Admin/Principal can mark for any section. A Teacher can only mark for sections
    where they are the assigned class teacher — students/parents never reach this view."""
    template_name = "attendance/mark_attendance.html"
    allowed_roles = MANAGEMENT_ROLES + ["TEACHER"]

    def get_allowed_sections(self, request):
        if request.user.is_superuser or request.user.role in MANAGEMENT_ROLES:
            return Section.objects.all()
        return Section.objects.filter(class_teacher__user=request.user)

    def get(self, request):
        sections = self.get_allowed_sections(request)
        section_id = request.GET.get("section")
        date_str = request.GET.get("date") or datetime.date.today().isoformat()
        students = []
        if section_id and sections.filter(id=section_id).exists():
            students = Student.objects.filter(section_id=section_id, status="ACTIVE")
            existing = {a.student_id: a.status for a in StudentAttendance.objects.filter(student__in=students, date=date_str)}
            for s in students:
                s.current_status = existing.get(s.id, "PRESENT")
        return render(request, self.template_name, {
            "sections": sections, "students": students,
            "selected_section": section_id, "selected_date": date_str,
            "status_choices": StudentAttendance.Status.choices,
        })

    def post(self, request):
        sections = self.get_allowed_sections(request)
        section_id = request.POST.get("section")
        if not sections.filter(id=section_id).exists():
            raise PermissionDenied("You can only mark attendance for your own section.")
        date_str = request.POST.get("date")
        student_ids = request.POST.getlist("student_id")
        for sid in student_ids:
            status = request.POST.get(f"status_{sid}", "PRESENT")
            StudentAttendance.objects.update_or_create(
                student_id=sid, date=date_str,
                defaults={"status": status, "marked_by": request.user},
            )
        messages.success(request, "Attendance saved successfully.")
        return redirect(f"/attendance/mark/?section={section_id}&date={date_str}")


class AttendanceReportView(RoleRequiredMixin, View):
    """Read-only report for staff. Students/parents use their own portal view instead."""
    template_name = "attendance/report.html"
    allowed_roles = MANAGEMENT_ROLES + ["TEACHER"]

    def get(self, request):
        sections = self.get_allowed_sections(request)
        section_id = request.GET.get("section")
        records = StudentAttendance.objects.select_related("student").all().order_by("-date")[:200]
        if not (request.user.is_superuser or request.user.role in MANAGEMENT_ROLES):
            records = records.filter(student__section__in=sections)
        if section_id:
            records = records.filter(student__section_id=section_id)
        return render(request, self.template_name, {"records": records, "sections": sections, "selected_section": section_id})

    def get_allowed_sections(self, request):
        if request.user.is_superuser or request.user.role in MANAGEMENT_ROLES:
            return Section.objects.all()
        return Section.objects.filter(class_teacher__user=request.user)
