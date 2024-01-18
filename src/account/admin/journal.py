from typing import Any
from django.contrib import admin
from account.models import AccountJournal
from django.utils import timezone
from account.models import Expense

@admin.register(AccountJournal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ['type', 'created_by', 'created_at']
    fields = ['type']


    def save_model(self, request, obj, form, change) -> None:
        super().save_model(request, obj, form, change)
        if obj.type == 'daily':
            expenses =  Expense.objects.filter(date=timezone.now().date(), is_approved=True)
        else:
            expenses = Expense.objects.filter(date__month=timezone.now().month, is_approved=True)
        obj.expenses.set(expenses)