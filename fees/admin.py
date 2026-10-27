from django.contrib import admin
from .models import FeeStructure, FeePayment, Income, Expense

admin.site.register(FeeStructure)
admin.site.register(FeePayment)
admin.site.register(Income)
admin.site.register(Expense)
