"""Helpers for scoping what a logged-in user may touch (used by exams, homework, hifz, etc.)."""
from django.db.models import Q

from .mixins import MANAGEMENT_ROLES


def is_management(user):
    return user.is_authenticated and (user.is_superuser or user.role in MANAGEMENT_ROLES)


def teacher_profile(user):
    return getattr(user, "teacher_profile", None) if user.is_authenticated else None


def allowed_sections(user, strict=False):
    """Sections a user may work with: all for management. For a teacher: the sections where they are
    class teacher, plus (unless strict=True) every section of a class in which they teach a subject
    (subjects are assigned per class, not per section). strict=True is used for sensitive per-student
    records such as Quran progress."""
    from academics.models import Section
    if is_management(user):
        return Section.objects.select_related("school_class").all()
    t = teacher_profile(user)
    if user.role == "TEACHER" and t:
        cond = Q(class_teacher=t) if strict else (Q(class_teacher=t) | Q(school_class__subjects__teacher=t))
        return Section.objects.select_related("school_class").filter(cond).distinct()
    return Section.objects.none()


def allowed_students(user, strict=False):
    from students.models import Student
    return Student.objects.filter(section__in=allowed_sections(user, strict=strict))


def allowed_subjects(user, school_class):
    """Subjects of `school_class` the user may enter marks / homework for."""
    from academics.models import Subject, Section
    qs = Subject.objects.filter(school_class=school_class)
    if is_management(user):
        return qs
    t = teacher_profile(user)
    if user.role == "TEACHER" and t:
        if Section.objects.filter(school_class=school_class, class_teacher=t).exists():
            return qs
        return qs.filter(teacher=t)
    return qs.none()


def student_for_user(user):
    return getattr(user, "student_profile", None) if user.is_authenticated else None


def family_students(user):
    """Students a STUDENT/PARENT user may view (own record / linked children)."""
    from students.models import Student
    if user.role == "STUDENT":
        s = student_for_user(user)
        return Student.objects.filter(pk=s.pk) if s else Student.objects.none()
    if user.role == "PARENT":
        return Student.objects.filter(parent=user)
    return Student.objects.none()
