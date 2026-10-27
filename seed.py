"""
Seed script for the Jamia Rahmania Rizvia Sohawa Management System.
Run with: python manage.py shell < seed.py
"""
import os
import django
import datetime
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from accounts.models import User
from academics.models import AcademicYear, SchoolClass, Section, Subject
from teachers.models import Teacher
from students.models import Student
from fees.models import FeeStructure, FeePayment, Income, Expense
from attendance.models import StudentAttendance
from notices.models import Notice, Event
from sitepages.models import SiteSettings

print("Seeding database...")

# Superuser
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser(username="admin", password="admin123", role=User.Role.SUPER_ADMIN, email="admin@jrrs.example")
    print("Created superuser: admin / admin123")

# Academic year
year, _ = AcademicYear.objects.get_or_create(
    name="2026-2027",
    defaults={"start_date": datetime.date(2026, 4, 1), "end_date": datetime.date(2027, 3, 31), "is_current": True},
)

# Classes & sections
class_names = ["Nazra", "Hifz", "Tajweed", "Dars-e-Nizami Year 1", "Dars-e-Nizami Year 2"]
sections = []
for cname in class_names:
    sc, _ = SchoolClass.objects.get_or_create(name=cname, academic_year=year)
    for sec_name in ["A", "B"]:  # e.g. morning / evening batch
        sec, _ = Section.objects.get_or_create(school_class=sc, name=sec_name)
        sections.append(sec)

# Teachers
teacher_names = [("Qari Muhammad", "Ali"), ("Maulana Ahmed", "Raza"), ("Qari Bilal", "Hussain"), ("Maulana Usman", "Farooq")]
teachers = []
for i, (fn, ln) in enumerate(teacher_names, start=1):
    username = f"teacher{i}"
    if not User.objects.filter(username=username).exists():
        u = User.objects.create_user(username=username, password="changeme123", first_name=fn, last_name=ln, role=User.Role.TEACHER, email=f"{username}@jrrs.example")
    else:
        u = User.objects.get(username=username)
    t, _ = Teacher.objects.get_or_create(user=u, defaults={
        "employee_id": f"EMP-{1000+i}", "qualification": "Shahadat-ul-Alamiyyah", "experience_years": random.randint(2, 15),
        "salary": random.randint(40000, 90000), "date_joined": datetime.date(2022, 1, 1),
    })
    teachers.append(t)

for i, sec in enumerate(sections):
    sec.class_teacher = teachers[i % len(teachers)]
    sec.save()

# Subjects
subject_list = ["Quran (Nazra / Hifz)", "Tajweed", "Arabic", "Fiqh", "Urdu", "English", "Mathematics"]
for sc in SchoolClass.objects.all():
    for j, sub in enumerate(subject_list):
        Subject.objects.get_or_create(name=sub, code=f"{sc.pk}-{sub[:3].upper()}", school_class=sc,
                                       defaults={"teacher": teachers[j % len(teachers)]})

# Students
first_names = ["Ahmed", "Zainab", "Hamza", "Fatima", "Omar", "Maryam", "Usman", "Hira", "Abdullah", "Aisha"]
last_names = ["Raza", "Sheikh", "Chaudhry", "Baig", "Farooq"]
students = []
for i in range(1, 41):
    fn = random.choice(first_names)
    ln = random.choice(last_names)
    adm = f"JRR-{2026000+i}"
    sec = random.choice(sections)
    s, created = Student.objects.get_or_create(admission_number=adm, defaults={
        "roll_number": str(i), "first_name": fn, "last_name": ln,
        "date_of_birth": datetime.date(2015, random.randint(1, 12), random.randint(1, 28)),
        "gender": random.choice(["M", "F"]), "section": sec,
        "guardian_name": f"Mr. {ln}", "guardian_relation": "Father", "guardian_phone": "0300-0000000",
    })
    students.append(s)

# Fee structures & payments
for sc in SchoolClass.objects.all():
    fs, _ = FeeStructure.objects.get_or_create(school_class=sc, name="Monthly Tuition Fee", defaults={"amount": 3500, "frequency": "MONTHLY"})
    for st in Student.objects.filter(section__school_class=sc)[:8]:
        paid = random.choice([3500, 3500, 0, 1500])
        FeePayment.objects.get_or_create(
            student=st, fee_structure=fs, due_date=datetime.date.today(),
            defaults={
                "amount_due": 3500, "amount_paid": paid,
                "status": "PAID" if paid == 3500 else ("PARTIAL" if paid else "PENDING"),
                "paid_on": datetime.date.today() if paid else None,
                "receipt_number": f"RCPT-{st.admission_number}" if paid else None,
            },
        )

# Attendance for last 10 days
today = datetime.date.today()
for i in range(10):
    d = today - datetime.timedelta(days=i)
    for st in students:
        StudentAttendance.objects.get_or_create(student=st, date=d, defaults={"status": random.choice(["PRESENT", "PRESENT", "PRESENT", "ABSENT", "LATE"])})

# Notices & events
Notice.objects.get_or_create(title="Welcome to the New Academic Year 2026-2027", defaults={"content": "We welcome all students and staff to the new academic year. May Allah grant everyone success.", "audience": "ALL", "is_pinned": True})
Event.objects.get_or_create(title="Annual Quran Competition", defaults={"date": today + datetime.timedelta(days=20), "location": "Jamia Masjid Gulzar-e-Rehmat", "description": "Hifz and Qira'at competition for all students."})

# Sample student login + linked parent login (for testing role-based portal access)
demo_student = students[0]
if not demo_student.user_id:
    su = User.objects.create_user(username="student1", password="changeme123", first_name=demo_student.first_name,
                                   last_name=demo_student.last_name, role=User.Role.STUDENT, email="student1@jrrs.example")
    demo_student.user = su
if not User.objects.filter(username="parent1").exists():
    pu = User.objects.create_user(username="parent1", password="changeme123", first_name="Guardian", last_name="One",
                                   role=User.Role.PARENT, email="parent1@jrrs.example")
else:
    pu = User.objects.get(username="parent1")
demo_student.parent = pu
demo_student.save()

# Sample accountant login
if not User.objects.filter(username="accountant1").exists():
    User.objects.create_user(username="accountant1", password="changeme123", first_name="Finance", last_name="Officer",
                              role=User.Role.ACCOUNTANT, email="accountant1@jrrs.example")

# Sample income / funding records
income_samples = [
    ("Haji Abdul Rehman", "ZAKAT", 50000),
    ("Mrs. Nasreen Bibi", "SADQA", 5000),
    ("Anonymous Donor", "SADQA_E_FITAR", 15000),
    ("Malik Farms", "USHAR", 30000),
    ("Alumni Association", "DONATION", 25000),
]
for donor, itype, amount in income_samples:
    Income.objects.get_or_create(donor_name=donor, income_type=itype, amount=amount,
                                  defaults={"date": today - datetime.timedelta(days=random.randint(0, 25))})

# Public-site contact details (edit anytime from /admin/ > Sitepages > Site Settings).
# Bank details are intentionally left blank — enter the real account in the admin panel.
SiteSettings.objects.update_or_create(pk=1, defaults={
    "phone": "+92 344 5681779",
    "email": "mssialvi721@gmail.com",
    "address": "Near Jamia Masjid Gulzar-e-Rehmat, close to the main Sohawa Bus Stop, G.T. Road, Sohawa, Jhelum",
    "facebook_url": "https://www.facebook.com/RehmaniaSohawa/",
    "whatsapp_number": "923445681779",
    "website_url": "http://jamiarehmaniarizviasohawa.weebly.com/",
    "established_year": 1988,
    "founder_name": "Hazrat Allama Qari Abdullah Sialvi",
})

# ---- Exams & results (first exam published so the student portal has something to show)
from exams.models import Exam, ExamResult
from timetable.models import Period
from homework.models import Homework
from library.models import Book, BookIssue
from inventory.models import Item, StockMovement
from hifz.models import HifzRecord

first_class = SchoolClass.objects.order_by("id").first()
first_section = Section.objects.filter(school_class=first_class).first()
# make sure the demo student (student1 / parent1) has a section with results, homework and timetable
for st in students[:3]:
    st.section = first_section
    st.save()
exam, _ = Exam.objects.get_or_create(
    name="Monthly Test", school_class=first_class,
    defaults={"start_date": today - datetime.timedelta(days=10), "end_date": today - datetime.timedelta(days=8), "is_published": True},
)
for st in Student.objects.filter(section__school_class=first_class):
    for sub in Subject.objects.filter(school_class=first_class):
        ExamResult.objects.get_or_create(exam=exam, student=st, subject=sub,
                                         defaults={"total_marks": 100, "obtained_marks": random.randint(35, 98)})

# ---- Timetable (Saturday–Thursday style week; Friday off) for the first section
subs = list(Subject.objects.filter(school_class=first_class))
slots = [(datetime.time(8, 0), datetime.time(8, 45)), (datetime.time(8, 45), datetime.time(9, 30)), (datetime.time(10, 0), datetime.time(10, 45))]
for day in [5, 6, 0, 1, 2, 3]:
    for i, (a, b) in enumerate(slots):
        sub = subs[(day + i) % len(subs)]
        Period.objects.get_or_create(section=first_section, day=day, start_time=a,
                                     defaults={"end_time": b, "subject": sub, "teacher": sub.teacher})

# ---- Homework
if first_section and not Homework.objects.exists():
    Homework.objects.create(section=first_section, subject=subs[0], title="Revise this week's lesson",
                            description="Recite the lesson 5 times before the next class.",
                            due_date=today + datetime.timedelta(days=3), assigned_by=User.objects.get(username="teacher1"))

# ---- Library
for title, author, cat, lang, copies in [
    ("Tafseer Ibn Kathir (Urdu)", "Hafiz Ibn Kathir", "Tafseer", "Urdu", 2),
    ("Riyad-us-Saliheen", "Imam Nawawi", "Hadith", "Arabic", 3),
    ("Seerat-un-Nabi", "Allama Shibli Nomani", "Seerah", "Urdu", 2),
    ("Bahishti Zewar", "Maulana Ashraf Ali Thanvi", "Fiqh", "Urdu", 4),
]:
    Book.objects.get_or_create(title=title, defaults={"author": author, "category": cat, "language": lang, "copies": copies})
if not BookIssue.objects.exists():
    BookIssue.objects.create(book=Book.objects.first(), student=students[1],
                             issued_on=today - datetime.timedelta(days=5), due_date=today + datetime.timedelta(days=9))

# ---- Inventory
for name, cat, qty, mn, unit in [
    ("Quran Qaida", "BOOKS", 40, 10, "pcs"), ("Whiteboard markers", "BOOKS", 6, 10, "pcs"),
    ("Prayer mats", "PRAYER", 25, 5, "pcs"), ("Desks / Rehal", "FURNITURE", 60, 0, "pcs"),
]:
    Item.objects.get_or_create(name=name, defaults={"category": cat, "quantity": qty, "min_quantity": mn, "unit": unit})

# ---- Quran progress for the demo student
if not HifzRecord.objects.exists():
    for k, kind in enumerate(["SABAQ", "SABQI", "MANZIL"]):
        HifzRecord.objects.create(student=demo_student, kind=kind, para=3 + k, portion="Page 1-2",
                                  performance="GOOD", recorded_by=User.objects.get(username="teacher1"))

print("Seeding complete!")
print("Login as admin: admin / admin123")
print("Login as teacher: teacher1 / changeme123")
print(f"Login as student: student1 / changeme123  (record: {demo_student.admission_number})")
print("Login as parent: parent1 / changeme123  (linked to student1's child)")
print("Login as accountant: accountant1 / changeme123")
