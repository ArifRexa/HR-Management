import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from account.models import AccountJournal, Income, Expense
from django.utils import timezone
from django.template.loader import get_template
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from weasyprint import HTML
from django.db.models.functions import TruncDate, Concat, ExtractYear, ExtractMonth
from django.db.models import Sum, Count, Value, CharField, Min
from django.db.models import DateField
from django.db.models import F, ExpressionWrapper, DecimalField, Q
from datetime import date, timedelta,datetime
from itertools import zip_longest


@require_http_methods(["POST", "GET"])
@login_required(login_url="/admin/login/")
def payment_voucher(request, id):
    voucher = get_object_or_404(AccountJournal, id=id)
    expenses = voucher.expenses.values('expanse_group__account_code', 'expanse_group__title') \
                                .annotate(expense_amount=Sum('amount')) \
                                .order_by('expanse_group__account_code') \
                            .values('expanse_group__account_code', 'expanse_group__title', 'expense_amount').exclude(add_to_balance_sheet=False)
    

    #generate pv id / pv no
    id_list = []
    current_month = datetime.now().month
    get_current_month_voucher = AccountJournal.objects.filter(date__month= current_month,type='daily')\
    .order_by('date').values_list('id')

    for d in get_current_month_voucher:
        id_list.append(int(d[0]))
    index_of_id = int(id_list.index(id)) + 1

    date_in_str = str(voucher.date) 
    date_obj = datetime.strptime(date_in_str, "%Y-%m-%d")
    month = date_obj.strftime("%m")
    year = date_obj.strftime("%y")
    pv_no = f"{month}{year}/P00{index_of_id}"


    #get all notes for daily expense
    expense_note = ''

    # Query Expense objects for the given date and concatenate notes
    get_expense_notes = Expense.objects.filter(date=voucher.date)

    for index, note in enumerate(get_expense_notes):
        expense_note += note.note
        # Add comma if it's not the last note
        if index < len(get_expense_notes) - 1:
            expense_note += ', '

    # Print the concatenated notes

    template = get_template('pdf/payment_voucher.html')
    # get the context data
    context = {'voucher': voucher, 'expenses': expenses,'pv_no':pv_no,'expense_note':expense_note}
    
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
    expense_dates = monthly_journal.expenses.filter(date__year=monthly_journal.date.year, date__month=monthly_journal.date.month) \
                                .annotate(day=TruncDate('date', output_field=DateField())) \
                                .annotate(year=ExtractYear('date')) \
                                .values('day', 'year') \
                                .annotate(count=Count('id'), daily_expenses=Sum('amount')) \
                                .order_by('day') \
                                .values('day', 'year', 'daily_expenses')
    
    expenses_data = {}

    for expense_date in expense_dates:
        expenses = monthly_journal.expenses.filter(Q(date=expense_date['day']) & Q(add_to_balance_sheet=True) & Q(is_approved=True)) \
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
# def account_journal(request, id):
#     monthly_journal = get_object_or_404(AccountJournal, id=id)
    
#     # get the template
#     template = get_template('excel/account-journal.html')
    
#     # data calculation 
#     # expense_dates = monthly_journal.expenses.annotate(day=TruncDate('date')) \
#     #                             .values('day') \
#     #                             .annotate(count=Count('id'), daily_expenses=Sum('amount')) \
#     #                             .order_by('day') \
#     #                             .values('day', 'daily_expenses')
#     expense_dates = monthly_journal.expenses.annotate(day=TruncDate('date', output_field=DateField())) \
#                                 .annotate(year=ExtractYear('date')) \
#                                 .values('day', 'year') \
#                                 .annotate(count=Count('id'), daily_expenses=Sum('amount')) \
#                                 .order_by('day') \
#                                 .values('day', 'year', 'daily_expenses')
    
#     expenses_data = {}

#     for expense_date in expense_dates:
#         expenses = monthly_journal.expenses.filter(date=expense_date['day']) \
#                                         .values('expanse_group__account_code', 'expanse_group__title') \
#                                         .order_by('expanse_group__account_code') \
#                                         .annotate(expense_amount=Sum('amount')) \
#                                         .values('expense_amount') \
#                                         .values('expanse_group__id', 'expanse_group__account_code', 'expanse_group__title', 'expense_amount')              
#         key = str(expense_date['day'])
#         value = expenses
#         expenses_data[key] = value

#     # get the context data
#     context = {'expense_data': expenses_data}

#     # Render the html template with the context data.
#     html_content = template.render(context)
   
#     # Create a response with the Excel file
#     file_name = str(timezone.now())
#     response = HttpResponse(html_content, content_type='application/vnd.ms-excel')
#     response['Content-Disposition'] = f'attachment; filename=account-journal-{file_name}.xls'
#     return response 

@require_http_methods(["POST", "GET"])
@login_required(login_url="/admin/login/")
def costs_by_expense_group(request, id):
    monthly_journal = get_object_or_404(AccountJournal, id=id)
    
    # get the template
    template = get_template('excel/monthly-expense-group.html')
    
    # data calculation 
    expenses_data = monthly_journal.expenses.filter(Q(add_to_balance_sheet=True) & Q(is_approved=True) & Q(date__year=monthly_journal.date.year) & Q(date__month=monthly_journal.date.month))\
                                .values('expanse_group__account_code') \
                                .annotate(expense_amount=Sum('amount'),
                                        vds_rate=F('expanse_group__vds_rate'),
                                        tds_rate=F('expanse_group__tds_rate'),
                                        vds_amount=ExpressionWrapper((F('vds_rate') * F('expense_amount') / 100),
                                                output_field=DecimalField()),
                                        tds_amount=ExpressionWrapper((F('tds_rate') * F('expense_amount') / 100),
                                                output_field=DecimalField())) \
                                .order_by('expanse_group__account_code') \
                                .values('expanse_group__account_code', 'expanse_group__title', 'expense_amount','vds_rate', 'vds_amount', 'tds_rate', 'tds_amount')
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
def balance_sheet(request, id):
    monthly_journal = get_object_or_404(AccountJournal, id=id)
    template = get_template('excel/balance-sheet.html')

    # expenses_data = Expense.objects.filter(
    #     Q(add_to_balance_sheet = True) & 
    #     Q(is_approved = True) &
    #     Q(date__gte = monthly_journal.date - timedelta(days=30)) & 
    #     Q(date__lte = monthly_journal.date)
    # ).values('date','expanse_group__title', 'amount')\
    # .order_by('date')

    expenses_data = Expense.objects.filter(
        Q(add_to_balance_sheet=True) &
        Q(is_approved=True) &
        Q(date__year=monthly_journal.date.year) &
        Q(date__month=monthly_journal.date.month)
    ).values('expanse_group__title').annotate(
        total_amount=Sum('amount'),
    ).order_by('expanse_group__title')\

   

    total_expense_amount = expenses_data.aggregate(total_amount=Sum('amount'))['total_amount'] or 0

        
    incomes_data = Income.objects.filter(
        Q(add_to_balance_sheet = True) & 
        Q(status = "approved") &
        Q(date__year=monthly_journal.date.year) & 
        Q(date__month=monthly_journal.date.month)
    ).values('date','project__title', 'payment').order_by('date')

    total_income_amount = incomes_data.aggregate(total_amount=Sum('payment'))['total_amount'] or 0

    zipped_data = list(zip_longest(incomes_data, expenses_data, fillvalue={}))

    context = {
        'month' : monthly_journal.date.strftime("%B"),
        'year' : monthly_journal.date.strftime("%Y"),
        'total_expense_amount': total_expense_amount,
        'total_income_amount': total_income_amount,
        'zipped_data': zipped_data
        }

    # Render the html template with the context data.
    html_content = template.render(context)
   
    # Create a response with the Excel file
    file_name = str(timezone.now())
    response = HttpResponse(html_content, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename=income-statement -{file_name}.xls'
    return response 