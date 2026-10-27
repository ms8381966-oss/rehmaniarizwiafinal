import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse

from dashboard.tests import make_world
from .models import Book, BookIssue


class LibraryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.w = make_world()
        cls.book = Book.objects.create(title="Riyad-us-Saliheen", copies=1)

    def test_availability_and_return(self):
        today = datetime.date.today()
        issue = BookIssue(book=self.book, student=self.w["stu"], issued_on=today, due_date=today + datetime.timedelta(days=7))
        issue.full_clean()
        issue.save()
        self.assertEqual(self.book.available, 0)
        second = BookIssue(book=self.book, student=self.w["stu_other"], issued_on=today, due_date=today + datetime.timedelta(days=7))
        with self.assertRaises(ValidationError):
            second.full_clean()
        issue.returned_on = today
        issue.save()
        self.assertEqual(self.book.available, 1)

    def test_borrower_required_exactly_one(self):
        today = datetime.date.today()
        with self.assertRaises(ValidationError):
            BookIssue(book=self.book, issued_on=today, due_date=today).full_clean()

    def test_fine(self):
        today = datetime.date.today()
        issue = BookIssue.objects.create(book=self.book, student=self.w["stu"], issued_on=today - datetime.timedelta(days=20),
                                         due_date=today - datetime.timedelta(days=10))
        self.assertEqual(issue.overdue_days, 10)
        self.assertEqual(issue.fine, 50)
