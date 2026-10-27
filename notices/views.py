from accounts.mixins import RoleRequiredMixin, MANAGEMENT_ROLES
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Notice, Event
from .forms import NoticeForm, EventForm


class NoticeListView(RoleRequiredMixin, ListView):
    model = Notice
    template_name = "notices/notice_list.html"
    context_object_name = "notices"
    paginate_by = 15
    allowed_roles = ["SUPER_ADMIN", "PRINCIPAL", "ADMIN", "TEACHER", "STUDENT", "PARENT", "ACCOUNTANT", "LIBRARIAN", "STAFF"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_superuser and user.role not in MANAGEMENT_ROLES:
            audience_map = {"STUDENT": "STUDENTS", "PARENT": "PARENTS", "TEACHER": "TEACHERS", "STAFF": "STAFF"}
            aud = audience_map.get(user.role)
            qs = qs.filter(audience__in=[a for a in ["ALL", aud] if a])
        return qs


class NoticeCreateView(RoleRequiredMixin, CreateView):
    model = Notice
    form_class = NoticeForm
    template_name = "notices/generic_form.html"
    success_url = reverse_lazy("notices:list")
    extra_context = {"title": "Add Notice"}
    allowed_roles = MANAGEMENT_ROLES

    def form_valid(self, form):
        form.instance.published_by = self.request.user
        return super().form_valid(form)


class NoticeUpdateView(RoleRequiredMixin, UpdateView):
    model = Notice
    form_class = NoticeForm
    template_name = "notices/generic_form.html"
    success_url = reverse_lazy("notices:list")
    extra_context = {"title": "Edit Notice"}
    allowed_roles = MANAGEMENT_ROLES


class NoticeDeleteView(RoleRequiredMixin, DeleteView):
    model = Notice
    template_name = "notices/generic_confirm_delete.html"
    success_url = reverse_lazy("notices:list")
    allowed_roles = MANAGEMENT_ROLES


class EventListView(RoleRequiredMixin, ListView):
    model = Event
    template_name = "notices/event_list.html"
    context_object_name = "events"
    allowed_roles = ["SUPER_ADMIN", "PRINCIPAL", "ADMIN", "TEACHER", "STUDENT", "PARENT", "ACCOUNTANT", "LIBRARIAN", "STAFF"]


class EventCreateView(RoleRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = "notices/generic_form.html"
    success_url = reverse_lazy("notices:event_list")
    extra_context = {"title": "Add Event"}
    allowed_roles = MANAGEMENT_ROLES
