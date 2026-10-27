from django import forms
from accounts.utils import allowed_sections
from accounts.widgets import BootstrapModelForm
from academics.models import Subject
from .models import Homework


class HomeworkForm(BootstrapModelForm):
    class Meta:
        model = Homework
        fields = ["section", "subject", "title", "description", "assigned_on", "due_date", "attachment"]
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user is not None:
            self.fields["section"].queryset = allowed_sections(user)

    def clean(self):
        cleaned = super().clean()
        section, subject = cleaned.get("section"), cleaned.get("subject")
        if section and subject and subject.school_class_id != section.school_class_id:
            self.add_error("subject", "This subject does not belong to the selected section's class.")
        if cleaned.get("assigned_on") and cleaned.get("due_date") and cleaned["due_date"] < cleaned["assigned_on"]:
            self.add_error("due_date", "Due date cannot be before the assigned date.")
        return cleaned
