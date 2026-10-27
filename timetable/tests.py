import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError

from dashboard.tests import make_world
from .models import Period


class TimetableTests(TestCase):
    def test_teacher_double_booking_rejected(self):
        w = make_world()
        Period.objects.create(section=w["sec"], day=0, start_time=datetime.time(8), end_time=datetime.time(9), subject=w["subj"], teacher=w["teacher"])
        clash = Period(section=w["sec_other"], day=0, start_time=datetime.time(8, 30), end_time=datetime.time(9, 30), subject=w["subj"], teacher=w["teacher"])
        with self.assertRaises(ValidationError):
            clash.full_clean()

    def test_end_before_start_rejected(self):
        w = make_world()
        with self.assertRaises(ValidationError):
            Period(section=w["sec"], day=1, start_time=datetime.time(9), end_time=datetime.time(8)).full_clean()
