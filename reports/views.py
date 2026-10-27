import csv
import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from urllib.parse import quote

from accounts.mixins import RoleRequiredMixin, MANAGEMENT_ROLES, FINANCE_ROLES
from django.views import View

from students.models import Student
from attendance.models import StudentAttendance
from fees.models import FeePayment, Income, Expense

REPORT_TYPES = {
    "students": {"label": "Students", "date_field": "admission_date", "allowed_roles": MANAGEMENT_ROLES + ["TEACHER"]},
    "attendance": {"label": "Attendance", "date_field": "date", "allowed_roles": MANAGEMENT_ROLES + ["TEACHER"]},
    "fees": {"label": "Fee Payments", "date_field": "due_date", "allowed_roles": FINANCE_ROLES},
    "income": {"label": "Income & Funding", "date_field": "date", "allowed_roles": FINANCE_ROLES},
    "expenses": {"label": "Expenses", "date_field": "date", "allowed_roles": FINANCE_ROLES},
    "exams": {"label": "Exam Results", "date_field": "exam__start_date", "allowed_roles": MANAGEMENT_ROLES},
    "hifz": {"label": "Quran Progress", "date_field": "date", "allowed_roles": MANAGEMENT_ROLES + ["TEACHER"]},
    "inventory": {"label": "Inventory Stock", "date_field": None, "allowed_roles": MANAGEMENT_ROLES + ["STAFF"]},
    "library": {"label": "Library Issues", "date_field": "issued_on", "allowed_roles": MANAGEMENT_ROLES + ["LIBRARIAN"]},
}


def _get_queryset(report_type, start_date, end_date):
    if report_type == "students":
        qs = Student.objects.select_related("section", "section__school_class").all()
        if start_date:
            qs = qs.filter(admission_date__gte=start_date)
        if end_date:
            qs = qs.filter(admission_date__lte=end_date)
        
        rows = [["Admission #", "Name", "Section", "Gender", "Status", "Admission Date", "Guardian", "Guardian Phone"]]
        for s in qs:
            rows.append([s.admission_number, s.full_name, str(s.section or "-"), s.get_gender_display(),
                         s.get_status_display(), str(s.admission_date), s.guardian_name, s.guardian_phone, s])
        return rows

    if report_type == "attendance":
        qs = StudentAttendance.objects.select_related("student").all()
        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)
        rows = [["Date", "Student", "Admission #", "Status", "Remarks"]]
        for a in qs.order_by("-date"):
            rows.append([str(a.date), a.student.full_name, a.student.admission_number, a.get_status_display(), a.remarks])
        return rows

    if report_type == "fees":
        qs = FeePayment.objects.select_related("student", "fee_structure").all()
        if start_date:
            qs = qs.filter(due_date__gte=start_date)
        if end_date:
            qs = qs.filter(due_date__lte=end_date)
        rows = [["Receipt #", "Student", "Fee", "Amount Due", "Amount Paid", "Balance", "Status", "Due Date", "Paid On"]]
        for p in qs.order_by("-due_date"):
            rows.append([p.receipt_number or "-", p.student.full_name, p.fee_structure.name, str(p.amount_due),
                         str(p.amount_paid), str(p.balance()), p.get_status_display(), str(p.due_date), str(p.paid_on or "-")])
        return rows

    if report_type == "income":
        qs = Income.objects.all()
        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)
        rows = [["Date", "Donor / Source", "Type", "Amount", "Contact", "Notes"]]
        for i in qs.order_by("-date"):
            rows.append([str(i.date), i.donor_name, i.get_income_type_display(), str(i.amount), i.contact_number, i.notes])
        return rows

    if report_type == "expenses":
        qs = Expense.objects.all()
        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)
        rows = [["Date", "Title", "Category", "Amount", "Notes"]]
        for e in qs.order_by("-date"):
            rows.append([str(e.date), e.title, e.category, str(e.amount), e.notes])
        return rows

    if report_type == "exams":
        from exams.models import ExamResult
        qs = ExamResult.objects.select_related("exam", "student", "subject")
        if start_date:
            qs = qs.filter(exam__start_date__gte=start_date)
        if end_date:
            qs = qs.filter(exam__start_date__lte=end_date)
        rows = [["Exam", "Class", "Student", "Admission #", "Subject", "Obtained", "Total", "%", "Grade"]]
        for r in qs.order_by("exam__start_date", "student__admission_number", "subject__name"):
            rows.append([r.exam.name, r.exam.school_class.name, r.student.full_name, r.student.admission_number,
                         r.subject.name, str(r.obtained_marks), str(r.total_marks), str(r.percentage), r.grade])
        return rows

    if report_type == "hifz":
        from hifz.models import HifzRecord
        qs = HifzRecord.objects.select_related("student")
        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)
        rows = [["Date", "Student", "Admission #", "Type", "Para", "Portion", "Performance", "Remarks"]]
        for h in qs:
            rows.append([str(h.date), h.student.full_name, h.student.admission_number, h.get_kind_display(),
                         str(h.para), h.portion, h.get_performance_display(), h.remarks])
        return rows

    if report_type == "inventory":
        from inventory.models import Item
        rows = [["Item", "Category", "Quantity", "Unit", "Min. Level", "Location", "Low Stock"]]
        for i in Item.objects.all():
            rows.append([i.name, i.get_category_display(), str(i.quantity), i.unit, str(i.min_quantity), i.location, "Yes" if i.is_low else "No"])
        return rows

    if report_type == "library":
        from library.models import BookIssue
        qs = BookIssue.objects.select_related("book", "student", "teacher__user")
        if start_date:
            qs = qs.filter(issued_on__gte=start_date)
        if end_date:
            qs = qs.filter(issued_on__lte=end_date)
        rows = [["Book", "Borrower", "Issued", "Due", "Returned", "Fine (Rs)"]]
        for i in qs:
            rows.append([i.book.title, str(i.borrower), str(i.issued_on), str(i.due_date), str(i.returned_on or "-"), str(i.fine)])
        return rows

    return [["No data"]]

class ReportsIndexView(RoleRequiredMixin, View):
    template_name = "reports/index.html"
    allowed_roles = MANAGEMENT_ROLES + ["TEACHER", "ACCOUNTANT"]

    def get(self, request):
        user = request.user
        available = {}
        for key, meta in REPORT_TYPES.items():
            if user.is_superuser or user.role in meta["allowed_roles"]:
                available[key] = meta["label"]
        
        selected_type = request.GET.get("type")
        start_date = request.GET.get("start_date") or None
        end_date = request.GET.get("end_date") or None
        
        report_data = None
        if selected_type and selected_type in available:
            report_data = _get_queryset(selected_type, start_date, end_date)
            
            # Text Sheet Summary Generation Logic
            if selected_type == "students" and len(report_data) > 1:
                from exams.models import ExamResult
                
                for row in report_data[1:]:
                    student_instance = row[8]  # Extracting actual student object instance cleanly
                    
                    # Fetch student's available exam entries sorted by latest dates
                    student_results = ExamResult.objects.filter(student=student_instance).select_related('exam', 'subject').order_by('-exam__start_date')
                    
                    if student_results.exists():
                        latest_exam_name = student_results.first().exam.name
                        # Filter rows strictly specific to the most recent exam context
                        exam_specific_results = student_results.filter(exam__name=latest_exam_name)
                        
                        sheet_lines = [f"Result Sheet - {latest_exam_name}:"]
                        grand_total = 0
                        grand_obtained = 0
                        
                        for r in exam_specific_results:
                            sheet_lines.append(f"• {r.subject.name}: {r.obtained_marks:.0f}/{r.total_marks:.0f} ({r.grade})")
                            grand_total += r.total_marks
                            grand_obtained += r.obtained_marks
                        
                        if grand_total > 0:
                            total_percentage = (grand_obtained / grand_total) * 100
                            sheet_lines.append(f"Grand Total: {grand_obtained:.0f}/{grand_total:.0f} ({total_percentage:.1f}%)")
                        
                        # Pack complete multi-subject performance lines string onto template object property
                        student_instance.recent_result_summary = "\n".join(sheet_lines)
                    else:
                        student_instance.recent_result_summary = ""

        context = {
            "report_types": available,
            "selected_type": selected_type,
            "report_rows": report_data[1:] if report_data else None,
            "report_header": report_data if report_data else None,
            "start_date": start_date,
            "end_date": end_date,
        }
        return render(request, self.template_name, context)


class ReportsExportView(RoleRequiredMixin, View):
    allowed_roles = MANAGEMENT_ROLES + ["TEACHER", "ACCOUNTANT"]

    def get(self, request):
        report_type = request.GET.get("type")
        fmt = request.GET.get("format", "csv")
        start_date = request.GET.get("start_date") or None
        end_date = request.GET.get("end_date") or None

        meta = REPORT_TYPES.get(report_type)
        if not meta:
            return HttpResponse("Invalid report type.", status=400)
        if not (request.user.is_superuser or request.user.role in meta["allowed_roles"]):
            return HttpResponse("You do not have permission to export this report.", status=403)

        rows = _get_queryset(report_type, start_date, end_date)
        filename_bits = [report_type]
        if start_date:
            filename_bits.append(f"from-{start_date}")
        if end_date:
            filename_bits.append(f"to-{end_date}")
        filename = "_".join(filename_bits) or report_type

        cleaned_rows = []
        for index, r in enumerate(rows):
            if index == 0:
                cleaned_rows.append(r)
            else:
                cleaned_rows.append(r[:8] if report_type == "students" else r)

        if fmt == "csv":
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
            writer = csv.writer(response)
            writer.writerows(cleaned_rows)
            return response
            
        if fmt == "pdf":
            return HttpResponse("PDF export not implemented yet.", status=501)


class GenerateWhatsAppReportView(RoleRequiredMixin, View):
    allowed_roles = MANAGEMENT_ROLES + ["TEACHER"]

    def get(self, request):
        student_id = request.GET.get("student_id")
        result_text = request.GET.get("result", "").strip()
        custom_note = request.GET.get("note", "").strip()

        if not student_id:
            return JsonResponse({"error": "Student ID is required"}, status=400)

        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return JsonResponse({"error": "Student not found"}, status=404)

        # Phone number se saare extra spaces aur symbols saaf karein
        raw_phone = "".join(filter(str.isdigit, student.guardian_phone))
        
        # SMART COUNTRY CODE CHECK: Agar number 03 se shuru ho raha hai, toh 0 hata kar 92 lagayein
        if raw_phone.startswith("03"):
            phone_number = "92" + raw_phone[1:]
        elif raw_phone.startswith("3"):
            phone_number = "92" + raw_phone
        else:
            phone_number = raw_phone

        message = f"Assalam-o-Alaikum,\n\nHere is the performance report for {student.full_name}:\n"
        
        if result_text:
            message += f"\n{result_text}\n"
        if custom_note:
            message += f"\nTeacher Note: {custom_note}\n"
            
        message += f"\nRegards,\nSchool Management"

        encoded_message = quote(message)
        
        # FIXED DESKTOP ROUTING URL: Bina extra trailing slash ke strict send parameter queries mapping
        whatsapp_url = f"https://web.whatsapp.com/send/?phone={phone_number}&text={encoded_message}"
        return JsonResponse({
            "success": True,
            "whatsapp_url": whatsapp_url
        })
