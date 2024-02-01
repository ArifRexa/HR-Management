from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from account.models import AccountJournal
from django.utils import timezone
from django.template.loader import get_template
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from weasyprint import HTML
from django.db.models.functions import TruncDate, Concat
from django.db.models import Sum, Count, Value, CharField

@require_http_methods(["POST", "GET"])
@login_required(login_url="/admin/login/")
def payment_voucher(request, id):
    voucher = get_object_or_404(AccountJournal, id=id)
    expenses = voucher.expenses.values('expanse_group__account_code', 'expanse_group__title') \
                                .annotate(expense_amount=Sum('amount')) \
                                .order_by('expanse_group__account_code') \
                                .values('expanse_group__account_code', 'expanse_group__title', 'expense_amount')
    
    # get the template
    template = get_template('pdf/payment_voucher.html')

    # get the context data
    context = {'voucher': voucher, 'expenses': expenses}
    
    # Render the html template with the context data.
    html_content = template.render(context)

    # Create weasyprint object from the html
    html = HTML(string=html_content)

    # generate pdf
    pdf_file = html.write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    filename = str(timezone.now())
    response['Content-Disposition'] = f'attachment; filename="payment-voucher-{filename}.pdf"'
    
    return response

@require_http_methods(["POST", "GET"])
@login_required(login_url="/admin/login/")
def account_journal(request, id):
    monthly_journal = get_object_or_404(AccountJournal, id=id)
    
    # get the template
    template = get_template('excel/account-journal.html')
    
    # data calculation 
    expense_dates = monthly_journal.expenses.annotate(day=TruncDate('date')) \
                                .values('day') \
                                .annotate(count=Count('id'), daily_expenses=Sum('amount')) \
                                .order_by('day') \
                                .values('day', 'daily_expenses')
    
    expenses_data = {}

    for expense_date in expense_dates:
        expenses = monthly_journal.expenses.filter(date=expense_date['day']) \
                                        .values('expanse_group__account_code', 'expanse_group__title') \
                                        .order_by('expanse_group__account_code') \
                                        .annotate(expense_amount=Sum('amount')) \
                                        .values('expense_amount') \
                                        .values('expanse_group__id', 'expanse_group__account_code', 'expanse_group__title', 'expense_amount')              
        key = str(expense_date['day'])
        value = expenses
        expenses_data[key] = value

    # get the context data
    context = {'expense_data': expenses_data}

    # Render the html template with the context data.
    html_content = template.render(context)
   
    # Create a response with the Excel file
    file_name = str(timezone.now())
    response = HttpResponse(html_content, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename=account-journal-{file_name}.xls'
    return response 

@require_http_methods(["POST", "GET"])
@login_required(login_url="/admin/login/")
def costs_by_expense_group(request, id):
    monthly_journal = get_object_or_404(AccountJournal, id=id)
    
    # get the template
    template = get_template('excel/monthly-expense-group.html')
    
    # data calculation 
    expenses_data = monthly_journal.expenses.values('expanse_group__account_code') \
                                .annotate(expense_amount=Sum('amount')) \
                                .order_by('expanse_group__account_code') \
                                .values('expanse_group__account_code', 'expanse_group__title', 'expense_amount')
    

    # get the context data
    context = {'expense_data': expenses_data}

    # Render the html template with the context data.
    html_content = template.render(context)
   
    # Create a response with the Excel file
    file_name = str(timezone.now())
    response = HttpResponse(html_content, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename=account-journal-{file_name}.xls'
    return response 