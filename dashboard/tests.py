"""Smoke tests: every page loads for the roles that should see it, and is blocked for the others."""
import datetime

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from academics.models import AcademicYear, SchoolClass, Section, Subject
from teachers.models import Teacher
from students.models import Student


def make_world():
    year = AcademicYear.objects.create(name="2026-2027", start_date=datetime.date(2026, 4, 1), end_date=datetime.date(2027, 3, 31), is_current=True)
    cls = SchoolClass.objects.create(name="Hifz", academic_year=year)
    users = {}
    for role in ["SUPER_ADMIN", "PRINCIPAL", "ADMIN", "TEACHER", "STUDENT", "PARENT", "ACCOUNTANT", "LIBRARIAN", "STAFF"]:
        users[role] = User.objects.create_user(username=role.lower(), password="pw12345!x", role=role)
    t = Teacher.objects.create(user=users["TEACHER"], employee_id="T1", date_joined=datetime.date(2024, 1, 1))
    other_user = User.objects.create_user(username="other_teacher", password="pw12345!x", role="TEACHER")
    other_t = Teacher.objects.create(user=other_user, employee_id="T2", date_joined=datetime.date(2024, 1, 1))
    cls2 = SchoolClass.objects.create(name="Nazra", academic_year=year)
    sec = Section.objects.create(school_class=cls, name="A", class_teacher=t)
    sec_other = Section.objects.create(school_class=cls2, name="A", class_teacher=other_t)
    subj = Subject.objects.create(name="Quran", code="Q1", school_class=cls, teacher=t)
    Subject.objects.create(name="Quran", code="Q2", school_class=cls2, teacher=other_t)
    stu = Student.objects.create(admission_number="JRR-1", first_name="Ali", last_name="Khan", date_of_birth=datetime.date(2015, 1, 1),
                                 gender="M", section=sec, user=users["STUDENT"], parent=users["PARENT"])
    stu_other = Student.objects.create(admission_number="JRR-2", first_name="Bilal", last_name="Raza", date_of_birth=datetime.date(2015, 1, 1),
                                       gender="M", section=sec_other)
    return {"users": users, "cls": cls, "sec": sec, "sec_other": sec_other, "subj": subj, "stu": stu, "stu_other": stu_other, "teacher": t, "other_teacher": other_t}


class PageAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.w = make_world()

    def get(self, role, url):
        self.client.logout()
        self.client.login(username=role.lower(), password="pw12345!x")
        return self.client.get(url)

    def test_public_pages(self):
        for name in ["sitepages:about", "sitepages:services", "sitepages:contact", "accounts:login"]:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_contact_form_saves_message(self):
        from sitepages.models import ContactMessage
        r = self.client.post(reverse("sitepages:contact"), {"name": "Zahid", "message": "Salam, admission info please", "phone": "0300"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_staff_pages_load(self):
        urls = [reverse(n) for n in [
            "exams:list", "homework:list", "hifz:list", "timetable:view", "library:books",
            "inventory:list", "certificates:list", "dashboard:index", "students:list",
        ]]
        for role in ["SUPER_ADMIN", "PRINCIPAL", "ADMIN"]:
            for u in urls:
                self.assertEqual(self.get(role, u).status_code, 200, f"{role} {u}")

    def test_blocked_pages(self):
        blocked = {
            "STUDENT": ["exams:list", "hifz:list", "library:books", "inventory:list", "certificates:list"],
            "PARENT": ["exams:list", "hifz:list", "library:books", "inventory:list", "certificates:list"],
            "TEACHER": ["certificates:list", "inventory:list"],
            "ACCOUNTANT": ["exams:list", "certificates:list", "inventory:list"],
            "LIBRARIAN": ["exams:list", "certificates:list"],
        }
        for role, names in blocked.items():
            for n in names:
                self.assertEqual(self.get(role, reverse(n)).status_code, 403, f"{role} {n}")

    def test_family_pages_load(self):
        for role in ["STUDENT", "PARENT"]:
            for n in ["homework:list", "timetable:view"]:
                self.assertEqual(self.get(role, reverse(n)).status_code, 200, f"{role} {n}")
        self.assertEqual(self.get("STUDENT", reverse("portal:home")).status_code, 200)
        self.assertEqual(self.get("PARENT", reverse("portal:child_detail", args=[self.w["stu"].pk])).status_code, 200)

    def test_librarian_and_staff_modules(self):
        self.assertEqual(self.get("LIBRARIAN", reverse("library:books")).status_code, 200)
        self.assertEqual(self.get("LIBRARIAN", reverse("library:issues")).status_code, 200)
        self.assertEqual(self.get("STAFF", reverse("inventory:list")).status_code, 200)
        self.assertEqual(self.get("TEACHER", reverse("library:issues")).status_code, 403)
