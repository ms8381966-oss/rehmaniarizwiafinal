from django.db import models


class FeeStructure(models.Model):
    school_class = models.ForeignKey("academics.SchoolClass", on_delete=models.CASCADE, related_name="fee_structures")
    name = models.CharField(max_length=100)  # e.g. Tuition Fee, Admission Fee
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=[("MONTHLY", "Monthly"), ("QUARTERLY", "Quarterly"), ("ANNUAL", "Annual"), ("ONE_TIME", "One Time")])

    def __str__(self):
        return f"{self.name} - {self.school_class}"


class FeePayment(models.Model):
    class Status(models.TextChoices):
        PAID = "PAID", "Paid"
        PARTIAL = "PARTIAL", "Partial"
        PENDING = "PENDING", "Pending"

    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="fee_payments")
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name="payments")
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    paid_on = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    receipt_number = models.CharField(max_length=30, unique=True, blank=True, null=True)

    class Meta:
        ordering = ["-due_date"]

    def balance(self):
        return (self.amount_due + self.fine - self.discount) - self.amount_paid

    def __str__(self):
        return f"{self.student} - {self.fee_structure.name}"


class Income(models.Model):
    """Tracks funding the school receives — donations, religious giving, and other income."""
    class IncomeType(models.TextChoices):
        ZAKAT = "ZAKAT", "Zakat"
        SADQA = "SADQA", "Sadqa"
        SADQA_E_FITAR = "SADQA_E_FITAR", "Sadqa-e-Fitar"
        USHAR = "USHAR", "Ushar"
        FEE = "FEE", "Fee"
        DONATION = "DONATION", "General Donation"
        OTHER = "OTHER", "Other"

    donor_name = models.CharField(max_length=150, help_text="Who gave this income")
    income_type = models.CharField(max_length=20, choices=IncomeType.choices, default=IncomeType.DONATION)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    contact_number = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.donor_name} - {self.get_income_type_display()} - {self.amount}"


class Expense(models.Model):
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.title} - {self.amount}"
