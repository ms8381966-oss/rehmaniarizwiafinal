from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView

from accounts.decorators import role_required
from accounts.mixins import RoleRequiredMixin, MANAGEMENT_ROLES
from .forms import CertificateForm
from .models import Certificate


class CertificateListView(RoleRequiredMixin, ListView):
    model = Certificate
    template_name = "certificates/certificate_list.html"
    context_object_name = "certificates"
    paginate_by = 25
    allowed_roles = MANAGEMENT_ROLES

    def get_queryset(self):
        return Certificate.objects.select_related("student")


class CertificateCreateView(RoleRequiredMixin, CreateView):
    model = Certificate
    form_class = CertificateForm
    template_name = "partials/form.html"
    success_url = reverse_lazy("certificates:list")
    extra_context = {"title": "Issue Certificate"}
    allowed_roles = MANAGEMENT_ROLES

    def get_initial(self):
        initial = super().get_initial()
        if self.request.GET.get("student"):
            initial["student"] = self.request.GET["student"]
        return initial

    def form_valid(self, form):
        form.instance.issued_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("certificates:print", args=[self.object.pk])


class CertificateDeleteView(RoleRequiredMixin, DeleteView):
    model = Certificate
    template_name = "partials/confirm_delete.html"
    success_url = reverse_lazy("certificates:list")
    allowed_roles = MANAGEMENT_ROLES


@role_required(*MANAGEMENT_ROLES)
def certificate_print(request, pk):
    cert = get_object_or_404(Certificate.objects.select_related("student__section__school_class"), pk=pk)
    return render(request, "certificates/certificate_print.html", {"cert": cert, "student": cert.student})
