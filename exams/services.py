"""Result calculations shared by the exams app and the student/parent portal."""
from decimal import Decimal

from .models import Exam, ExamResult, PASS_PERCENT, grade_for


def student_summary(exam, student):
    """Returns (results, totals) for one student in one exam. totals is None if no marks exist."""
    results = list(ExamResult.objects.filter(exam=exam, student=student).select_related("subject"))
    if not results:
        return results, None
    total = sum(r.total_marks for r in results)
    obtained = sum(r.obtained_marks for r in results)
    pct = (Decimal(obtained) / Decimal(total) * 100).quantize(Decimal("0.1")) if total else Decimal("0")
    failed_subjects = [r.subject.name for r in results if not r.passed]
    return results, {
        "total": total, "obtained": obtained, "percentage": pct, "grade": grade_for(pct),
        "passed": not failed_subjects, "failed_subjects": failed_subjects,
    }


def class_ranking(exam):
    """{student_id: (position, percentage)} for everyone with marks in this exam."""
    agg = {}
    for r in ExamResult.objects.filter(exam=exam):
        a = agg.setdefault(r.student_id, [Decimal("0"), 0])
        a[0] += r.obtained_marks
        a[1] += r.total_marks
    scored = sorted(
        ((sid, (o / t * 100) if t else Decimal("0")) for sid, (o, t) in agg.items()),
        key=lambda x: x[1], reverse=True,
    )
    ranking, last_pct, last_pos = {}, None, 0
    for i, (sid, pct) in enumerate(scored, start=1):
        if pct != last_pct:
            last_pos, last_pct = i, pct
        ranking[sid] = (last_pos, pct.quantize(Decimal("0.1")))
    return ranking


def published_exams_for(student):
    return Exam.objects.filter(is_published=True, results__student=student).distinct()
