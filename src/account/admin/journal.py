from typing import Any
from django.contrib import admin
from account.models import AccountJournal, Expense, MonthlyJournal, DailyPaymentVoucher
from django import forms
from django.utils.html import format_html
from django.db.models import Sum

class MonthlyJournalForm(forms.ModelForm):
    class Meta:
        model = MonthlyJournal
        fields = ['date']

    # def clean(self):
    #     clean_data = super().clean()
    #     has_journal = AccountJournal.objects.filter(date__month=clean_data.get('date').month, type='monthly').exists()
    #     if self.instance.id == None and has_journal:
    #         raise forms.ValidationError({'date': 'You have created this month journal. Try to create another month!'})
        
    def clean(self):
        clean_data = super().clean()
        date = clean_data.get('date')
        if date:
            month = date.month
            year = date.year
            has_journal = AccountJournal.objects.filter(date__month=month, date__year=year, type='monthly').exists()
            if self.instance.id is None and has_journal:
                raise forms.ValidationError({'date': 'You have already created a journal for this month. Try to create another month!'})
        return clean_data    
        
@admin.register(MonthlyJournal)
class MonthlyJournalAdmin(admin.ModelAdmin):
    # list_display = ['date', 'type', 'debit', 'credit', 'created_by', 'export_btn']
    list_display = ['date', 'export_btn', 'created_by']
    ordering = ['-date']
    date_hierarchy = 'date'
    list_filter = ['type', 'date']
    form = MonthlyJournalForm

    # def debit(self, obj=None):
    #     return obj.expenses.all().aggregate(debit=Sum('amount')).get('debit')
    
    # def credit(self, obj=None):
    #     return obj.expenses.all().aggregate(debit=Sum('amount')).get('debit')
    
    def save_model(self, request, obj, form, change) -> None:
        obj.type = 'monthly'
        super().save_model(request, obj, form, change)
        expenses = Expense.objects.filter(date__month=obj.date.month, is_approved=True)
        obj.expenses.set(expenses)

    @admin.display(description='Export File')
    def export_btn(self, obj: AccountJournal=None):
        url = obj.get_monthly_journal()
        group_costs = obj.group_cost_url()
        balance_sheet = obj.balance_sheet_url()
        monthly_expense = obj.get_monthly_expense_url()
        # monthly_expense_attachment = obj.get_monthly_expense_attachment_url()
        btn = f"""
            <a href="{url}" class="button" style="padding: 6px;text-decoration: none;">&#x2913; Account Journal</a>
            <a href="{group_costs}" class="button" style="padding: 6px;text-decoration: none;">&#x2913; Group Costs</a>
            <a href="{balance_sheet}" class="button" style="padding: 6px;text-decoration: none;">&#x2913; Income Statement </a>
            <a href="{monthly_expense}" class="button" style="padding: 6px;text-decoration: none;">&#x2913; ME - Date </a>
            <a href="{monthly_expense}?order_by=amount" class="button" style="padding: 6px;text-decoration: none;">&#x2913; ME - Amount </a>
            
            """
            # <a href="{monthly_expense_attachment}" class="button" style="padding: 6px;text-decoration: none;">&#x2913; MA - Date </a>
            # <a href="{monthly_expense_attachment}?order_by=amount" class="button" style="padding: 6px;text-decoration: none;">&#x2913; MA - Amount </a>
    
        return format_html(btn)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(type='monthly')


class DailyPaymentVoucherForm(forms.ModelForm):
    class Meta:
        model = DailyPaymentVoucher
        fields = ['date', 'note']

    def clean(self):
        clean_data = super().clean()
        has_journal = AccountJournal.objects.filter(date=clean_data.get('date'), type='daily').exists()
        if self.instance.id == None and has_journal:
            raise forms.ValidationError({'date': 'You have already created voucher of this day!'})
        
@admin.register(DailyPaymentVoucher)
class DailyPaymentVoucherAdmin(admin.ModelAdmin):
    list_display = ['date', 'pv_no', 'debit', 'credit', 'created_by', 'export_btn']
    date_hierarchy = 'date'
    ordering = ['-date']
    form = DailyPaymentVoucherForm

    def debit(self, obj=None):
        return obj.expenses.all().aggregate(debit=Sum('amount')).get('debit')
    
    def credit(self, obj=None):
        return obj.expenses.all().aggregate(debit=Sum('amount')).get('debit')
    
    @admin.display(description='Export Voucher')
    def export_btn(self, obj=None):
        url_payment = obj.get_pdf_generate_url_payment()
        url_journal = obj.get_pdf_generate_url_journal()
        btn = f"""
            <a href="{url_payment}" class="button" style="padding: 6px;text-decoration: none;">&#x2913; Payment Voucher</a>
            <a href="{url_journal}" class="button" style="padding: 6px;text-decoration: none;">&#x2913; Journal Voucher</a>
            """
        return format_html(btn)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(type='daily')
    
    def save_model(self, request, obj, form, change):
        obj.type = 'daily'
        super().save_model(request, obj, form, change)
        expenses =  Expense.objects.filter(date=obj.date, is_approved=True)
        vouchers = AccountJournal.objects.filter(type='daily', date__month=obj.date.month).count()
        if change == False:
            obj.pv_no = vouchers
        obj.save()
        obj.expenses.set(expenses)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'note':
            formfield.widget.attrs['placeholder'] = """You have the flexibility to include a note if you'd like. When choosing the daily payment voucher option, you can provide a brief description of your daily expenses if you wish."""
        return formfield