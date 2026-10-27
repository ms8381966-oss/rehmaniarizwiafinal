from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from academics.models import Section
from accounts.mixins import RoleRequiredMixin, MANAGEMENT_ROLES
from accounts.utils import family_students, is_management, teacher_profile

from .forms import PeriodForm
from .models import Period


def _build_grid(periods):
    slots = sorted({(p.start_time, p.end_time) for p in periods})
    days = sorted({p.day for p in periods})
    lookup = {}
    for p in periods:
        lookup.setdefault((p.start_time, p.end_time, p.day), []).append(p)
    rows = [{"start": s, "end": e, "cells": [lookup.get((s, e, d), []) for d in days]} for s, e in slots]
    return [dict(Period.Day.choices)[d] for d in days], rows


@login_required
def timetable_view(request):
    user = request.user
    if user.is_superuser or user.role not in ("STUDENT", "PARENT"):
        sections = Section.objects.select_related("school_class").all()
    else:
        sections = Section.objects.filter(students__in=family_students(user)).distinct()
    section = None
    if request.GET.get("section"):
        section = get_object_or_404(sections, pk=request.GET["section"])
    elif sections:
        section = sections.first()
    periods = list(Period.objects.filter(section=section).select_related("subject", "teacher__user")) if section else []
    day_names, rows = _build_grid(periods)
    return render(request, "timetable/timetable.html", {
        "sections": sections, "section": section, "day_names": day_names, "rows": rows,
        "can_edit": is_management(user), "periods": periods,
    })


@login_required
def my_schedule(request):
    t = teacher_profile(request.user)
    if not t:
        raise PermissionDenied("Only teachers have a personal schedule.")
    periods = list(Period.objects.filter(teacher=t).select_related("section__school_class", "subject"))
    day_names, rows = _build_grid(periods)
    return render(request, "timetable/my_schedule.html", {"day_names": day_names, "rows": rows})


class PeriodCreateView(RoleRequiredMixin, CreateView):
    model = Period
    form_class = PeriodForm
    template_name = "partials/form.html"
    extra_context = {"title": "Add Period"}
    allowed_roles = MANAGEMENT_ROLES

    def get_initial(self):
        initial = super().get_initial()
        if self.request.GET.get("section"):
            initial["section"] = self.request.GET["section"]
        return initial

    def get_success_url(self):
        return f"{reverse_lazy('timetable:view')}?section={self.object.section_id}"


class PeriodUpdateView(RoleRequiredMixin, UpdateView):
    model = Period
    form_class = PeriodForm
    template_name = "partials/form.html"
    extra_context = {"title": "Edit Period"}
    allowed_roles = MANAGEMENT_ROLES

    def get_success_url(self):
        return f"{reverse_lazy('timetable:view')}?section={self.object.section_id}"


class PeriodDeleteView(RoleRequiredMixin, DeleteView):
    model = Period
    template_name = "partials/confirm_delete.html"
    allowed_roles = MANAGEMENT_ROLES

    def get_success_url(self):
        return f"{reverse_lazy('timetable:view')}?section={self.object.section_id}"
