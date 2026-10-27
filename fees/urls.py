from django.urls import path
from . import views

app_name = "fees"

urlpatterns = [
    path("structures/", views.FeeStructureListView.as_view(), name="structure_list"),
    path("structures/add/", views.FeeStructureCreateView.as_view(), name="structure_add"),

    path("payments/", views.FeePaymentListView.as_view(), name="payment_list"),
    path("payments/collect/", views.FeePaymentCreateView.as_view(), name="payment_add"),
    path("payments/<int:pk>/edit/", views.FeePaymentUpdateView.as_view(), name="payment_edit"),

    path("income/", views.IncomeListView.as_view(), name="income_list"),
    path("income/add/", views.IncomeCreateView.as_view(), name="income_add"),

    path("expenses/", views.ExpenseListView.as_view(), name="expense_list"),
    path("expenses/add/", views.ExpenseCreateView.as_view(), name="expense_add"),
]
