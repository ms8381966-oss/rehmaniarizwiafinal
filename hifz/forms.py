from accounts.utils import allowed_students
from accounts.widgets import BootstrapModelForm
from .models import HifzRecord


class HifzForm(BootstrapModelForm):
    class Meta:
        model = HifzRecord
        fields = ["student", "date", "kind", "para", "portion", "performance", "remarks"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["student"].queryset = allowed_students(user, strict=True).filter(status="ACTIVE")
