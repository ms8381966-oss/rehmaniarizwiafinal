from accounts.widgets import BootstrapModelForm
from .models import Period


class PeriodForm(BootstrapModelForm):
    class Meta:
        model = Period
        fields = ["section", "day", "start_time", "end_time", "subject", "teacher", "room"]
