import datetime
from .models import SiteSettings


def site_settings(request):
    """Makes `site_settings` available in every template (footer contact info, etc.)."""
    s = SiteSettings.get_solo()
    years = max(datetime.date.today().year - s.established_year, 0)
    return {"site_settings": s, "years_of_service": years}
