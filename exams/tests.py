import datetime
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from dashboard.tests import make_world
from .models import Exam, ExamResult, grade_for
from .services import student_summary, class_ranking


class ExamLogicTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.w = make_world()
        cls.exam = Exam.objects.create(name="Mid", school_class=cls.w["cls"], start_date=datetime.date(2026, 9, 1))

    def login(self, role):
        self.client.logout()
        self.client.login(username=role.lower(), password="pw12345!x")

    def test_grades(self):
        self.assertEqual(grade_for(95), "A+")
        self.assertEqual(grade_for(40), "E")
        self.assertEqual(grade_for(39.9), "F")

    def test_summary_and_rank(self):
        ExamResult.objects.create(exam=self.exam, student=self.w["stu"], subject=self.w["subj"], total_marks=100, obtained_marks=80)
        ExamResult.objects.create(exam=self.exam, student=self.w["stu_other"], subject=self.w["subj"], total_marks=100, obtained_marks=30)
        _, totals = student_summary(self.exam, self.w["stu"])
        self.assertEqual(totals["percentage"], Decimal("80.0"))
        self.assertTrue(totals["passed"])
        rank = class_ranking(self.exam)
        self.assertEqual(rank[self.w["stu"].pk][0], 1)
        self.assertEqual(rank[self.w["stu_other"].pk][0], 2)
        _, t2 = student_summary(self.exam, self.w["stu_other"])
        self.assertFalse(t2["passed"])

    def test_teacher_enters_marks_for_own_section_only(self):
        self.login("TEACHER")
        url = reverse("exams:marks", args=[self.exam.pk])
        ok = self.client.post(f"{url}?section={self.w['sec'].pk}&subject={self.w['subj'].pk}",
                              {"total_marks": "50", f"marks_{self.w['stu'].pk}": "45"})
        self.assertEqual(ok.status_code, 302)
        r = ExamResult.objects.get(student=self.w["stu"])
        self.assertEqual((r.total_marks, r.obtained_marks), (50, Decimal("45")))
        # another teacher's section must be refused
        bad = self.client.get(f"{url}?section={self.w['sec_other'].pk}&subject={self.w['subj'].pk}")
        self.assertEqual(bad.status_code, 404)

    def test_marks_validation(self):
        self.login("TEACHER")
        url = reverse("exams:marks", args=[self.exam.pk]) + f"?section={self.w['sec'].pk}&subject={self.w['subj'].pk}"
        self.client.post(url, {"total_marks": "50", f"marks_{self.w['stu'].pk}": "75"})
        self.assertFalse(ExamResult.objects.exists())

    def test_report_card_visibility(self):
        ExamResult.objects.create(exam=self.exam, student=self.w["stu"], subject=self.w["subj"], total_marks=100, obtained_marks=70)
        url = reverse("exams:report_card", args=[self.exam.pk, self.w["stu"].pk])
        self.login("STUDENT")
        self.assertEqual(self.client.get(url).status_code, 403)  # not published yet
        self.exam.is_published = True
        self.exam.save()
        self.assertEqual(self.client.get(url).status_code, 200)
        self.login("PARENT")
        self.assertEqual(self.client.get(url).status_code, 200)
        # a student must not see someone else's card
        other = reverse("exams:report_card", args=[self.exam.pk, self.w["stu_other"].pk])
        self.login("STUDENT")
        self.assertEqual(self.client.get(other).status_code, 403)
        self.login("TEACHER")
        self.assertEqual(self.client.get(other).status_code, 403)
        self.assertEqual(self.client.get(url).status_code, 200)
