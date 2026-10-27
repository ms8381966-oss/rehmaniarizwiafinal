from django import forms
from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ["user", "admission_date", "parent"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ["address"]:
                css = field.widget.attrs.get("class", "")
                if isinstance(field.widget, (forms.Select,)):
                    field.widget.attrs["class"] = (css + " form-select").strip()
                elif not isinstance(field.widget, forms.DateInput):
                    field.widget.attrs["class"] = (css + " form-control").strip()
