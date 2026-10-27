from django import forms
from .models import FeeStructure, FeePayment, Income, Expense


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "school_class": forms.Select(attrs={"class": "form-select"}),
            "frequency": forms.Select(attrs={"class": "form-select"}),
        }


class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        exclude = ["status", "receipt_number"]
        widgets = {
            "student": forms.Select(attrs={"class": "form-select"}),
            "fee_structure": forms.Select(attrs={"class": "form-select"}),
            "amount_due": forms.NumberInput(attrs={"class": "form-control"}),
            "amount_paid": forms.NumberInput(attrs={"class": "form-control"}),
            "discount": forms.NumberInput(attrs={"class": "form-control"}),
            "fine": forms.NumberInput(attrs={"class": "form-control"}),
            "due_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "paid_on": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        exclude = ["recorded_by"]
        widgets = {
            "donor_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Donor / contributor name"}),
            "income_type": forms.Select(attrs={"class": "form-select"}),
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "contact_number": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = "__all__"
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.TextInput(attrs={"class": "form-control"}),
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }
