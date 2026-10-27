import datetime
from django.test import TestCase
from django.urls import reverse

from dashboard.tests import make_world
from .models import Certificate


class CertificateTests(TestCase):
    def test_serial_and_print(self):
        w = make_world()
        c = Certificate.objects.create(student=w["stu"], kind="HIFZ", issue_date=datetime.date(2026, 10, 1))
        self.assertTrue(c.serial.startswith("JRR-2026-"))
        self.client.login(username="admin", password="pw12345!x")
        r = self.client.get(reverse("certificates:print", args=[c.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Hifz")
        self.assertContains(r, w["stu"].full_name)
        # teacher cannot print
        self.client.logout(); self.client.login(username="teacher", password="pw12345!x")
        self.assertEqual(self.client.get(reverse("certificates:print", args=[c.pk])).status_code, 403)
