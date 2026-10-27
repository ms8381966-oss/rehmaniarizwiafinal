from django import forms
from .models import StudentAttendance


class AttendanceFilterForm(forms.Form):
    section = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-select"}))
    date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))

    def __init__(self, *args, **kwargs):
        from academics.models import Section
        super().__init__(*args, **kwargs)
        self.fields["section"].choices = [("", "All Sections")] + [(s.id, str(s)) for s in Section.objects.all()]
