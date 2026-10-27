import datetime
from django.test import TestCase
from django.urls import reverse

from dashboard.tests import make_world
from .models import Homework


class HomeworkTests(TestCase):
    def test_teacher_assigns_and_student_sees_only_own_section(self):
        w = make_world()
        self.client.login(username="teacher", password="pw12345!x")
        d = datetime.date.today()
        r = self.client.post(reverse("homework:add"), {"section": w["sec"].pk, "subject": w["subj"].pk, "title": "Revise",
                                                        "assigned_on": d, "due_date": d + datetime.timedelta(days=2)})
        self.assertEqual(r.status_code, 302)
        Homework.objects.create(section=w["sec_other"], title="Other section HW", due_date=d)
        self.client.logout(); self.client.login(username="student", password="pw12345!x")
        r = self.client.get(reverse("homework:list"))
        self.assertContains(r, "Revise")
        self.assertNotContains(r, "Other section HW")
        # students cannot create
        self.assertEqual(self.client.get(reverse("homework:add")).status_code, 403)
