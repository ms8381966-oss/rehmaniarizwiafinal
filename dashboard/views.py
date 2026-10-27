import datetime
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Sum, Count

from students.models import Student
from teachers.models import Teacher
from academics.models import SchoolClass, Section, Subject
from attendance.models import StudentAttendance
from fees.models import FeePayment, Income, Expense
from notices.models import Notice, Event
from accounts.models import User
from django.db.models import F
from library.models import Book  # BookIssue hata diya gaya hai
from inventory.models import Item
from exams.models import Exam
from sitepages.models import ContactMessage


@login_required
def index(request):
    if request.user.role in ("STUDENT", "PARENT") and not request.user.is_superuser:
        return redirect("portal:home")
    today = datetime.date.today()
    month_start = today.replace(day=1)

    total_students = Student.objects.filter(status="ACTIVE").count()
    total_teachers = Teacher.objects.filter(is_active=True).count()
    total_staff = User.objects.filter(role=User.Role.STAFF).count()
    total_parents = User.objects.filter(role=User.Role.PARENT).count()
    total_classes = SchoolClass.objects.count()
    total_sections = Section.objects.count()
    total_subjects = Subject.objects.count()

    today_attendance = StudentAttendance.objects.filter(date=today)
    today_present = today_attendance.filter(status="PRESENT").count()
    today_total = today_attendance.count()
    today_pct = round((today_present / today_total) * 100, 1) if today_total else 0

    month_attendance = StudentAttendance.objects.filter(date__gte=month_start)
    month_present = month_attendance.filter(status="PRESENT").count()
    month_total = month_attendance.count()
    month_pct = round((month_present / month_total) * 100, 1) if month_total else 0

    fee_collected = FeePayment.objects.filter(paid_on__gte=month_start).aggregate(s=Sum("amount_paid"))["s"] or 0
    pending_fees = FeePayment.objects.filter(status__in=["PENDING", "PARTIAL"]).aggregate(
        s=Sum("amount_due")
    )["s"] or 0
    monthly_income = Income.objects.filter(date__gte=month_start).aggregate(s=Sum("amount"))["s"] or 0
    monthly_expenses = Expense.objects.filter(date__gte=month_start).aggregate(s=Sum("amount"))["s"] or 0
    profit = float(fee_collected) + float(monthly_income) - float(monthly_expenses)

    recent_admissions = Student.objects.order_by("-admission_date")[:5]
    recent_payments = FeePayment.objects.select_related("student").order_by("-paid_on")[:5]
    recent_income = Income.objects.order_by("-date")[:5]
    recent_notices = Notice.objects.order_by("-published_on")[:5]
    upcoming_events = Event.objects.filter(date__gte=today).order_by("date")[:5]

    # last 6 months attendance chart
    months, attendance_series = [], []
    for i in range(5, -1, -1):
        m = (today.replace(day=1) - datetime.timedelta(days=30 * i)).replace(day=1)
        m_next = (m.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
        qs = StudentAttendance.objects.filter(date__gte=m, date__lt=m_next)
        total = qs.count()
        present = qs.filter(status="PRESENT").count()
        months.append(m.strftime("%b"))
        attendance_series.append(round((present / total) * 100, 1) if total else 0)

    students_by_class = list(
        SchoolClass.objects.annotate(count=Count("sections__students")).values("name", "count")
    )

    context = {
        "total_books": Book.objects.count(),  # Total books count dashboard ke liye
        "for_sale_books": Book.objects.filter(sale_status="FOR_SALE").count(),
        "low_stock_items": Item.objects.filter(quantity__lte=F("min_quantity")).count(),
        "upcoming_exams": Exam.objects.filter(start_date__gte=today).count(),
        "unread_messages": ContactMessage.objects.filter(is_read=False).count(),
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_staff": total_staff,
        "total_parents": total_parents,
        "total_classes": total_classes,
        "total_sections": total_sections,
        "total_subjects": total_subjects,
        "today_present": today_present,
        "today_total": today_total,
        "today_pct": today_pct,
        "month_pct": month_pct,
        "fee_collected": fee_collected,
        "monthly_income": monthly_income,
        "pending_fees": pending_fees,
        "monthly_expenses": monthly_expenses,
        "profit": profit,
        "recent_admissions": recent_admissions,
        "recent_payments": recent_payments,
        "recent_income": recent_income,
        "recent_notices": recent_notices,
        "upcoming_events": upcoming_events,
        "chart_months": json.dumps(months),
        "chart_attendance": json.dumps(attendance_series),
        "chart_class_labels": json.dumps([c["name"] for c in students_by_class]),
        "chart_class_data": json.dumps([c["count"] for c in students_by_class]),
    }
    return render(request, "dashboard/index.html", context)