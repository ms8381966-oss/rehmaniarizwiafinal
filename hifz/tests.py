from django.test import TestCase
from django.urls import reverse

from dashboard.tests import make_world
from .models import HifzRecord


class HifzTests(TestCase):
    def test_teacher_scope_and_family_scope(self):
        w = make_world()
        self.client.login(username="teacher", password="pw12345!x")
        r = self.client.post(reverse("hifz:add"), {"student": w["stu"].pk, "date": "2026-10-01", "kind": "SABAQ", "para": 5, "performance": "GOOD"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(HifzRecord.objects.count(), 1)
        # student in someone else's section isn't selectable
        r = self.client.post(reverse("hifz:add"), {"student": w["stu_other"].pk, "date": "2026-10-01", "kind": "SABAQ", "para": 5, "performance": "GOOD"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(HifzRecord.objects.count(), 1)
        self.assertEqual(self.client.get(reverse("hifz:student", args=[w["stu_other"].pk])).status_code, 403)
        # student sees own progress only
        self.client.logout(); self.client.login(username="student", password="pw12345!x")
        self.assertEqual(self.client.get(reverse("hifz:student", args=[w["stu"].pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("hifz:student", args=[w["stu_other"].pk])).status_code, 403)

    def test_para_range(self):
        w = make_world()
        self.client.login(username="admin", password="pw12345!x")
        r = self.client.post(reverse("hifz:add"), {"student": w["stu"].pk, "date": "2026-10-01", "kind": "SABAQ", "para": 31, "performance": "GOOD"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(HifzRecord.objects.count(), 0)
