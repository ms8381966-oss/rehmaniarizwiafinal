from accounts.widgets import BootstrapModelForm
from .models import Exam


class ExamForm(BootstrapModelForm):
    class Meta:
        model = Exam
        fields = ["name", "school_class", "start_date", "end_date", "is_published"]
