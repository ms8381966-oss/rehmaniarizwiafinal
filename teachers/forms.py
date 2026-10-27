from django import forms
from django.contrib.auth import get_user_model
from .models import Teacher

User = get_user_model()


class TeacherUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone"]
        widgets = {f: forms.TextInput(attrs={"class": "form-control"}) for f in ["username", "first_name", "last_name", "phone"]}
        widgets["email"] = forms.EmailInput(attrs={"class": "form-control"})


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        exclude = ["user"]
        widgets = {
            "date_joined": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "qualification": forms.TextInput(attrs={"class": "form-control"}),
            "employee_id": forms.TextInput(attrs={"class": "form-control"}),
            "experience_years": forms.NumberInput(attrs={"class": "form-control"}),
            "salary": forms.NumberInput(attrs={"class": "form-control"}),
        }
