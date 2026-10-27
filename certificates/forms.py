from django import forms
from accounts.widgets import BootstrapModelForm
from .models import Certificate


class CertificateForm(BootstrapModelForm):
    class Meta:
        model = Certificate
        fields = ["student", "kind", "issue_date", "details"]
        widgets = {"details": forms.Textarea(attrs={"rows": 3})}
