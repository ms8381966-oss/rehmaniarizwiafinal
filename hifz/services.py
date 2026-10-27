from django.db.models import Count


def progress_summary(student):
    """Small summary used on the student's Quran-progress page and the portal."""
    qs = student.hifz_records.all()
    last_sabaq = qs.filter(kind="SABAQ").first()
    paras = sorted(set(qs.filter(kind="SABAQ").values_list("para", flat=True)))
    by_kind = {row["kind"]: row["n"] for row in qs.values("kind").annotate(n=Count("id"))}
    return {"last_sabaq": last_sabaq, "paras_studied": paras, "by_kind": by_kind, "total": qs.count()}
