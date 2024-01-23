from typing import Any
from django.contrib import admin
from django.db.models.fields import Field
from django.http.request import HttpRequest
from account.models import AccountJournal
from django.utils import timezone
from account.models import Expense
from django import forms
from django.utils.html import format_html
from django.db.models import Sum

class AccountJournalForm(forms.ModelForm):

    class Meta:
        model = AccountJournal
        fields = ['date', 'type', 'note']

    def clean(self):
        clean_data = super().clean()
        # If update later
        if self.instance and self.instance.id != None:
            if clean_data.get('type') == 'daily':
                if self.instance.date != timezone.now().date():
                    raise forms.ValidationError({'type': 'Altering the daily journal is prohibited.'})
            else:
                if self.instance.date.month != timezone.now().month:
                    raise forms.ValidationError({'type': 'Modifying the monthly journal is not allowed.'})
                
        # prevent create duplicate daily or monthly journal
        if clean_data.get('type') == 'daily' and not self.instance.id:
            if AccountJournal.objects.filter(date=timezone.now().date(), type='daily').exists():
                raise forms.ValidationError({'type': 'You are restricted from generating more than one daily report.'})
        if clean_data.get('type') == 'monthly' and not self.instance.id:
            if AccountJournal.objects.filter(date__month=timezone.now().month, type='monthly').exists():
                raise forms.ValidationError({'type': 'You are limited to generating only one monthly journal.'})


        return clean_data
@admin.register(AccountJournal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'type', 'debit', 'credit', 'pv_no', 'created_by', 'export_btn']
    ordering = ['-created_at']
    form = AccountJournalForm

    def debit(self, obj=None):
        return obj.expenses.all().aggregate(debit=Sum('amount')).get('debit')
    
    def credit(self, obj=None):
        return obj.expenses.all().aggregate(debit=Sum('amount')).get('debit')

    def save_model(self, request, obj, form, change) -> None:
        super().save_model(request, obj, form, change)
        if obj.type == 'daily':
            expenses =  Expense.objects.filter(date=timezone.now().date(), is_approved=True)
            vouchers = AccountJournal.objects.filter(type='daily').count()
            obj.pv_no = vouchers
            obj.save()
        else:
            expenses = Expense.objects.filter(date__month=timezone.now().month, is_approved=True)

        obj.expenses.set(expenses)

    @admin.display(description='Export File')
    def export_btn(self, obj=None):
        if obj.type == 'daily':
            url = obj.get_pdf_generate_url()
            btn = f"""
                <a href="{url}" class="button" style="padding: 6px;text-decoration: none;">&#x2913; Payment Voucher</a>
                """
        else:
            url = obj.get_monthly_journal()
            btn = f"""
                <a href="{url}" class="button" style="padding: 6px;text-decoration: none;">&#x2913; Account Journal</a>
                """
    
        return format_html(btn)
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        
        if db_field.name == 'note':
            formfield.widget.attrs['placeholder'] = """You have the flexibility to include a note if you'd like. When choosing the daily payment voucher option, you can provide a brief description of your daily expenses if you wish."""
        return formfield