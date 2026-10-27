# Jamia Rahmania Rizvia Sohawa — Management System

A Django-based management system for Jamia Rahmania Rizvia Sohawa (Sohawa, Jhelum — founded 1988 by
Hazrat Allama Qari Abdullah Sialvi) with role-based logins, a live dashboard, and modules for students,
teachers, classes/sections/subjects, attendance, exams & result cards, Quran progress (Sabaq / Sabqi /
Manzil), timetable, homework, library, inventory, certificates, fees, donations and notices/events.

## Tech Stack
- Backend: Python 3 + Django 6
- Database: SQLite by default (zero setup) — switchable to MySQL via `.env`
- Frontend: Bootstrap 5, Chart.js, Font Awesome (navy & gold theme)
- Auth: Django's built-in auth with a custom `User` model and 9 roles (Super Admin, Principal,
  Admin, Teacher, Student, Parent, Accountant, Librarian, Staff)

## New modules (added in this version)
- **Exams & Results** — create exams per class, enter marks per section/subject (teachers only for their
  own sections/subjects), result sheet with positions, printable **Result Card** (grade, pass/fail,
  class position). Results become visible to students/parents only after you tick *Published*.
  Grading: A+ ≥90, A ≥80, B ≥70, C ≥60, D ≥50, E ≥40, F <40 (pass mark 40% — change `PASS_PERCENT` in `exams/models.py`).
- **Quran Progress (Hifz)** — daily Sabaq / Sabqi / Manzil records per student (para 1–30, portion,
  performance). Class teachers record for their own sections; students/parents see it in the portal.
- **Timetable** — weekly grid per section (any days, so Friday-off weeks work), teacher clash detection,
  "My Schedule" for teachers, read-only view for students/parents.
- **Homework** — teachers assign homework (with optional file) to their sections; students/parents see their own section's.
- **Library** — books catalogue, issue/return to students or teachers, availability tracking, overdue fine (Rs 5/day — `FINE_PER_DAY` in `library/models.py`). Librarian role supported.
- **Inventory** — items with stock in/out history and low-stock warnings.
- **Certificates** — Character, Leaving, Hifz-e-Quran completion, Nazra completion and Merit certificates with auto serial numbers and a print-ready A4 page.
- **Website contact form** now saves messages (Admin → Sitepages → Contact messages); dashboard shows unread count.
- **Reports & Export** also covers Exam Results, Quran Progress, Inventory and Library (CSV/PDF).
- Public site rebranded for the Jamia, with Urdu name, WhatsApp / Facebook / website links, founder and establishment year — all editable in Admin → Site Settings.

## What's included (original modules)
- **Public website** (no login required): Home, About, Services, Contact — navy & gold themed,
  describes the school, and the About/Contact pages show live contact info, a Facebook link, and
  **bank account details for donations** (Zakat, Sadqa, etc.) — all editable from
  `/admin/ → Sitepages → Site Settings` without touching code.
- **Reports & Export**: any Management/Finance/Teacher user can go to **Reports & Export** in the
  sidebar, pick a data type (Students, Attendance, Fee Payments, Income & Funding, Expenses), an
  optional date range, and download it as **CSV or PDF** — filtered exactly to that range.
- **Income & Funding module**: records donations and religious giving — who gave it (donor name),
  the type (**Zakat, Sadqa, Sadqa-e-Fitar, Ushar, Fee, General Donation, Other**), amount, date,
  and contact info. Shows on the dashboard alongside fee income, and feeds into the monthly
  profit calculation (Fee income + Donations − Expenses).
- Custom role-based `User` model + login/logout/profile/change-password
- **Role-based access, enforced on the backend (not just hidden in the UI)**:
  - **Super Admin / Principal / Admin** — full access to every module.
  - **Accountant** — dashboard + fee structures/payments/expenses; no student/teacher/attendance management.
  - **Teacher** — can view students and mark attendance **only for the sections where they're the assigned
    class teacher**; cannot manage other teachers, academic setup, or fees.
  - **Student** — logs into a dedicated **read-only portal**: own profile, own attendance history, own fee
    status, notices/events aimed at students. Cannot mark attendance or edit anything.
  - **Parent** — same read-only portal, scoped to their linked children (linked via the admin panel).
  - Every list/create/update/delete view checks the logged-in user's role server-side
    (`accounts/mixins.py::RoleRequiredMixin`), and the sidebar only shows links a role can actually use.
- Dashboard with live stats (students, teachers, classes, attendance %, fee collection, pending
  fees, expenses, profit) and Chart.js line/pie charts (staff roles only)
- Students: registration, search, filter by status, detail profile, edit, delete
- Teachers: add (creates linked user account), profile, edit, delete
- Academic structure: Academic Years, Classes, Sections (with class teacher), Subjects
- Attendance: mark daily attendance per section (teacher's own sections only), attendance report/history
- Fees: fee structures per class, fee collection with auto receipt numbers and balance
  calculation, donation/income tracking (Zakat, Sadqa, Sadqa-e-Fitar, Ushar, Fee, Other), and
  expense tracking
- Notices & Events: notice board with audience targeting and pinning (auto-filtered per role), event calendar
- Django Admin panel enabled for every model (superuser has full access)
- Seed script with sample data (40 students, 4 teachers, Nazra/Hifz/Tajweed/Dars-e-Nizami classes, fee/attendance
  history, a notice, an event, and one sample login per role for testing)

## Tests
```bash
python manage.py test
```

## Getting started

```bash
cd jamia_rahmania_rizvia
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # edit if needed
python manage.py migrate
python manage.py shell < seed.py     # optional: creates sample data + admin login
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** — you'll be redirected to the login page.

### Default logins (created by `seed.py`)
| Role       | Username     | Password    | What they see |
|------------|--------------|-------------|----------------|
| Admin      | admin        | admin123    | Everything |
| Teacher    | teacher1     | changeme123 | Their own sections' students + attendance marking |
| Student    | student1     | changeme123 | Read-only: own attendance, fees, notices |
| Parent     | parent1      | changeme123 | Read-only: linked child's attendance & fees |
| Accountant | accountant1  | changeme123 | Fee structures, payments, expenses |

Bank/donation details are **not** pre-filled — enter the real account in `/admin/ → Sitepages → Site Settings`.
Change these passwords immediately in production. Visit `/` for the public website — the login link is in
the top-right of the navbar.

If you skip the seed script, create your own admin with:
```bash
python manage.py createsuperuser
```

## Switching to MySQL

1. Install MySQL server and create a database, e.g. `jamia_rahmania_rizvia`.
2. In `.env`, set:
   ```
   DB_ENGINE=mysql
   DB_NAME=jamia_rahmania_rizvia
   DB_USER=your_mysql_user
   DB_PASSWORD=your_mysql_password
   DB_HOST=localhost
   DB_PORT=3306
   ```
3. Make sure `mysqlclient` is installed (it's in `requirements.txt`; on Linux you may need
   `sudo apt install default-libmysqlclient-dev pkg-config build-essential` first).
4. Run `python manage.py migrate` again against the MySQL database.

## Project structure

```
jamia_rahmania_rizvia/
├── config/            # settings, root urls, wsgi/asgi
├── accounts/          # custom User model, login, profile
├── dashboard/         # dashboard view + stats/charts
├── students/          # student CRUD
├── teachers/          # teacher CRUD (creates linked user)
├── academics/         # academic years, classes, sections, subjects
├── attendance/        # mark attendance, attendance report
├── fees/              # fee structures, fee payments, expenses
├── notices/           # notice board, events
├── exams/ timetable/ homework/ library/ inventory/ certificates/ hifz/   # new modules
├── sitepages/         # public website + site settings + contact messages
├── templates/          # shared base.html + per-app templates
├── static/css/style.css
├── seed.py             # sample data generator
├── requirements.txt
└── .env.example
```

## Roles & permissions
Every view requires login (`@login_required` / `LoginRequiredMixin`). The `User.role` field and
`accounts/decorators.py::role_required` give you a starting point for restricting specific views
to specific roles (e.g. only Accountants can collect fees) — wire this up per-view as your
policies require. Django's admin panel already has full role separation via Django's built-in
permission/group system, which you can assign per role from `/admin/`.

## Still not built
Teacher attendance and teacher leave have database models and Admin screens but no dedicated pages yet;
hostel/boarding, staff payroll and SMS/WhatsApp notifications are not included.

## Security notes
- CSRF protection is on by default (Django middleware + `{% csrf_token %}` in every form)
- Passwords are hashed by Django's auth system
- The custom user model uses role-based access; extend `role_required` to lock down views per
  role before deploying
- Set `DEBUG=False` and a strong random `SECRET_KEY` before deploying to production
#   r a h m a n i a - r i z v i a 
 
 

library done...done
report send on whatsapp...done

25 oct
dummy db created by claude 14mb...done
homework section removed...done
sections and subjects options were already in classes so removed from sidebar...done
library store...done
dark theme...done