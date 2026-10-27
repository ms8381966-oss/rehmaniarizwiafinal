import uuid
from django.db.models import Sum
from accounts.mixins import RoleRequiredMixin, FINANCE_ROLES
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import FeeStructure, FeePayment, Income, Expense
from .forms import FeeStructureForm, FeePaymentForm, IncomeForm, ExpenseForm


class FeeStructureListView(RoleRequiredMixin, ListView):
    model = FeeStructure
    template_name = "fees/structure_list.html"
    context_object_name = "structures"
    allowed_roles = FINANCE_ROLES


class FeeStructureCreateView(RoleRequiredMixin, CreateView):
    model = FeeStructure
    form_class = FeeStructureForm
    template_name = "fees/generic_form.html"
    success_url = reverse_lazy("fees:structure_list")
    extra_context = {"title": "Add Fee Structure"}
    allowed_roles = FINANCE_ROLES


class FeePaymentListView(RoleRequiredMixin, ListView):
    model = FeePayment
    template_name = "fees/payment_list.html"
    context_object_name = "payments"
    paginate_by = 20
    allowed_roles = FINANCE_ROLES

    def get_queryset(self):
        qs = FeePayment.objects.select_related("student", "fee_structure").all()
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_choices"] = FeePayment.Status.choices
        return ctx


class FeePaymentCreateView(RoleRequiredMixin, CreateView):
    model = FeePayment
    form_class = FeePaymentForm
    template_name = "fees/generic_form.html"
    success_url = reverse_lazy("fees:payment_list")
    extra_context = {"title": "Collect Fee"}
    allowed_roles = FINANCE_ROLES

    def form_valid(self, form):
        payment = form.save(commit=False)
        payment.receipt_number = f"RCPT-{uuid.uuid4().hex[:8].upper()}"
        balance = (payment.amount_due + payment.fine - payment.discount) - payment.amount_paid
        if balance <= 0:
            payment.status = FeePayment.Status.PAID
        elif payment.amount_paid > 0:
            payment.status = FeePayment.Status.PARTIAL
        else:
            payment.status = FeePayment.Status.PENDING
        payment.save()
        messages.success(self.request, f"Fee recorded. Receipt: {payment.receipt_number}")
        return super().form_valid(form)


class FeePaymentUpdateView(RoleRequiredMixin, UpdateView):
    model = FeePayment
    form_class = FeePaymentForm
    template_name = "fees/generic_form.html"
    success_url = reverse_lazy("fees:payment_list")
    extra_context = {"title": "Update Payment"}
    allowed_roles = FINANCE_ROLES


class IncomeListView(RoleRequiredMixin, ListView):
    model = Income
    template_name = "fees/income_list.html"
    context_object_name = "incomes"
    paginate_by = 20
    allowed_roles = FINANCE_ROLES

    def get_queryset(self):
        qs = Income.objects.all()
        income_type = self.request.GET.get("income_type")
        if income_type:
            qs = qs.filter(income_type=income_type)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["type_choices"] = Income.IncomeType.choices
        ctx["total"] = self.get_queryset().aggregate(s=Sum("amount"))["s"] or 0
        return ctx


class IncomeCreateView(RoleRequiredMixin, CreateView):
    model = Income
    form_class = IncomeForm
    template_name = "fees/generic_form.html"
    success_url = reverse_lazy("fees:income_list")
    extra_context = {"title": "Record Income / Donation"}
    allowed_roles = FINANCE_ROLES

    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        messages.success(self.request, "Income recorded successfully.")
        return super().form_valid(form)


class ExpenseListView(RoleRequiredMixin, ListView):
    model = Expense
    template_name = "fees/expense_list.html"
    context_object_name = "expenses"
    allowed_roles = FINANCE_ROLES


class ExpenseCreateView(RoleRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "fees/generic_form.html"
    success_url = reverse_lazy("fees:expense_list")
    extra_context = {"title": "Add Expense"}
    allowed_roles = FINANCE_ROLES
