from itertools import zip_longest

import pandas as pd
from django.contrib.auth.decorators import login_required
from django.db.models import (
    Count,
    DateField,
    DecimalField,
    ExpressionWrapper,
    F,
    Q,
    Sum,
)
from django.db.models.functions import ExtractYear, TruncDate
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template, render_to_string
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from weasyprint import HTML

from account.models import AccountJournal, Expense, Income, MonthlyJournal
from config.settings import MEDIA_URL


def generate_voucher_pdf(voucher, voucher_type, template_name):
    expenses = (
        voucher.expenses.values("expanse_group__account_code", "expanse_group__title")
        .annotate(expense_amount=Sum("amount"))
        .order_by("expanse_group__account_code")
        .values("expanse_group__account_code", "expanse_group__title", "expense_amount")
        .exclude(add_to_balance_sheet=False)
    )

    # Generate voucher number
    id_list = []
    get_current_month_voucher = (
        AccountJournal.objects.filter(type="daily").order_by("date").values_list("id")
    )

    for d in get_current_month_voucher:
        id_list.append(int(d[0]))

    # index_of_id = int(id_list.index(1)) + 1
    index_of_id = 1

    date_obj = voucher.date
    month = date_obj.strftime("%m")
    year = date_obj.strftime("%y")
    pv_no = f"{month}{year}/{voucher_type}00{index_of_id}"

    # Get all notes for daily expense
    expense_note = ""
    get_expense_notes = Expense.objects.filter(date=voucher.date)

    for index, note in enumerate(get_expense_notes):
        expense_note += note.note
        if index < len(get_expense_notes) - 1:
            expense_note += ", "

    # Render the HTML template
    template = get_template(template_name)
    context = {
        "voucher": voucher,
        "expenses": expenses,
        "pv_no": pv_no,
        "expense_note": expense_note,
    }
    html_content = template.render(context)

    # Generate PDF
    html = HTML(string=html_content)
    pdf_file = html.write_pdf()
    response = HttpResponse(pdf_file, content_type="application/pdf")
    filename = str(timezone.now())
    response["Content-Disposition"] = (
        f'attachment; filename="{voucher_type.lower()}-voucher-{filename}.pdf"'
    )

    return response


@require_http_methods(["POST", "GET"])
@login_required(login_url="/admin/login/")
def payment_voucher(request, id):
    voucher = get_object_or_404(AccountJournal, id=id)
    return generate_voucher_pdf(voucher, "PV", "pdf/payment_voucher.html")


@require_http_methods(["POST", "GET"])
@login_required(login_url="/admin/login/")
def journal_voucher(request, id):
    voucher = get_object_or_404(AccountJournal, id=id)
    return generate_voucher_pdf(voucher, "JV", "pdf/journal_voucher.html")


@require_http_methods(["POST", "GET"])
@login_required(login_url="/admin/login/")
def account_journal(request, id):
    monthly_journal = get_object_or_404(AccountJournal, id=id)

    # get the template
    template = get_template("excel/account-journal.html")

    # data calculation
    expense_dates = (
        monthly_journal.expenses.filter(
            date__year=monthly_journal.date.year, date__month=monthly_journal.date.month
        )
        .annotate(day=TruncDate("date", output_field=DateField()))
        .annotate(year=ExtractYear("date"))
        .values("day", "year")
        .annotate(count=Count("id"), daily_expenses=Sum("amount"))
        .order_by("day")
        .values("day", "year", "daily_expenses")
    )

    expenses_data = {}

    for expense_date in expense_dates:
        expenses = (
            monthly_journal.expenses.filter(
                Q(date=expense_date["day"])
                & Q(add_to_balance_sheet=True)
                & Q(is_approved=True)
            )
            .values("expanse_group__account_code", "expanse_group__title")
            .order_by("expanse_group__account_code")
            .annotate(expense_amount=Sum("amount"))
            .values("expense_amount")
            .values(
                "expanse_group__id",
                "expanse_group__account_code",
                "expanse_group__title",
                "expense_amount",
            )
        )
        key = str(expense_date["day"])
        value = expenses
        expenses_data[key] = value

    # get the context data
    context = {"expense_data": expenses_data}

    # Render the html template with the context data.
    html_content = template.render(context)

    # Create a response with the Excel file
    file_name = str(timezone.now())
    response = HttpResponse(html_content, content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = (
        f"attachment; filename=account-journal-{file_name}.xls"
    )
    return response


@require_http_methods(["POST", "GET"])
@login_required(login_url="/admin/login/")
def costs_by_expense_group(request, id):
    monthly_journal = get_object_or_404(AccountJournal, id=id)

    # get the template
    template = get_template("excel/monthly-expense-group.html")

    # data calculation
    expenses_data = (
        monthly_journal.expenses.filter(
            Q(add_to_balance_sheet=True)
            & Q(date__year=monthly_journal.date.year)
            & Q(date__month=monthly_journal.date.month)
        )
        .values("expanse_group__account_code")
        .annotate(
            expense_amount=Sum("amount"),
            vds_rate=F("expanse_group__vds_rate"),
            tds_rate=F("expanse_group__tds_rate"),
            vds_amount=ExpressionWrapper(
                (F("vds_rate") * F("expense_amount") / 100), output_field=DecimalField()
            ),
            tds_amount=ExpressionWrapper(
                (F("tds_rate") * F("expense_amount") / 100), output_field=DecimalField()
            ),
        )
        .order_by("expanse_group__account_code")
        .values(
            "expanse_group__account_code",
            "expanse_group__title",
            "expense_amount",
            "vds_rate",
            "vds_amount",
            "tds_rate",
            "tds_amount",
        )
    )
    # get the context data
    context = {"expense_data": expenses_data}

    # Render the html template with the context data.
    html_content = template.render(context)

    # Create a response with the Excel file
    file_name = str(timezone.now())
    response = HttpResponse(html_content, content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = (
        f"attachment; filename=account-journal-{file_name}.xls"
    )
    return response


@require_http_methods(["POST", "GET"])
@login_required(login_url="/admin/login/")
def balance_sheet(request, id):
    monthly_journal = get_object_or_404(AccountJournal, id=id)
    template = get_template("excel/balance-sheet.html")

    # expenses_data = Expense.objects.filter(
    #     Q(add_to_balance_sheet = True) &
    #     Q(is_approved = True) &
    #     Q(date__gte = monthly_journal.date - timedelta(days=30)) &
    #     Q(date__lte = monthly_journal.date)
    # ).values('date','expanse_group__title', 'amount')\
    # .order_by('date')

    expenses_data = (
        Expense.objects.filter(
            Q(add_to_balance_sheet=True)
            & Q(is_approved=True)
            & Q(date__year=monthly_journal.date.year)
            & Q(date__month=monthly_journal.date.month)
        )
        .values("expanse_group__title")
        .annotate(
            total_amount=Sum("amount"),
        )
        .order_by("expanse_group__title")
    )

    total_expense_amount = (
        expenses_data.aggregate(total_amount=Sum("amount"))["total_amount"] or 0
    )

    incomes_data = (
        Income.objects.filter(
            Q(add_to_balance_sheet=True)
            & Q(status="approved")
            & Q(date__year=monthly_journal.date.year)
            & Q(date__month=monthly_journal.date.month)
        )
        .values("date", "project__title", "payment")
        .order_by("date")
    )

    total_income_amount = (
        incomes_data.aggregate(total_amount=Sum("payment"))["total_amount"] or 0
    )

    zipped_data = list(zip_longest(incomes_data, expenses_data, fillvalue={}))

    context = {
        "month": monthly_journal.date.strftime("%B"),
        "year": monthly_journal.date.strftime("%Y"),
        "total_expense_amount": total_expense_amount,
        "total_income_amount": total_income_amount,
        "zipped_data": zipped_data,
    }

    # Render the html template with the context data.
    html_content = template.render(context)

    # Create a response with the Excel file
    file_name = str(timezone.now())
    response = HttpResponse(html_content, content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = (
        f"attachment; filename=income-statement -{file_name}.xls"
    )
    return response


@require_http_methods(["GET"])
@login_required(login_url="/admin/login/")
def monthly_expense_statement(request, id, *args, **kwargs):
    monthly_journal = MonthlyJournal.objects.get(id=id)
    order_by = request.GET.get("order_by", "date")
    field_mapping = {"date": "created_at", "amount": "amount"}
    expense = (
        Expense.objects.filter(created_at__date=monthly_journal.created_at.date())
        .order_by(field_mapping.get(order_by))
        .values("date", "expanse_group__title", "expense_category__title", "amount")
    )
    df = pd.DataFrame(list(expense))
    df.rename(
        columns={
            "data": "Data",
            "expanse_group__title": "Expanse Group",
            "expense_category__title": "Expanse Category",
            "amount": "Amount",
        },
        inplace=True,
    )
    df.loc["Total"] = df.sum(numeric_only=True, axis=0)
    df = df.fillna("")
    df.at["Total", "Expanse Category"] = "Total"
    template = get_template("pdf/monthly_expense.html")
    context = {
        "table": df.to_html(index=False),
        "month": monthly_journal.created_at.strftime("%B"),
        "year": monthly_journal.created_at.strftime("%Y"),
    }
    html_content = template.render(context)
    file_name = (
        f"Monthly Expense order by {order_by} - {monthly_journal.created_at.date()}.pdf"
    )

    # Generate PDF
    html = HTML(string=html_content)
    pdf_file = html.write_pdf()
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{file_name}"'

    return response


@require_http_methods(["GET"])
@login_required(login_url="/admin/login/")
def monthly_expense_attachment(request, id, *args, **kwargs):
    monthly_journal = MonthlyJournal.objects.get(id=id)
    order_by = request.GET.get("order_by", "date")
    field_mapping = {"date": "created_at", "amount": "amount"}
    expense = (
        Expense.objects.filter(created_at__date=monthly_journal.created_at.date())
        .order_by(field_mapping.get(order_by))
        .annotate(file=F("expanseattachment__attachment"))
        .values_list("file", flat=True)
    )
    expense_attachment_list = []
    for relpath in expense:
        if relpath:
            # Ensure a leading slash, in case MEDIA_URL doesn't
            rel_url = relpath if relpath.startswith("/") else MEDIA_URL + relpath
            abs_url = request.build_absolute_uri(rel_url)
            expense_attachment_list.append(abs_url)

    context = {
        "expenses": expense_attachment_list,
        "month": monthly_journal.created_at.strftime("%B"),
        "year": monthly_journal.created_at.strftime("%Y"),
    }
    html_content = render_to_string(
        "pdf/monthly_expense_attachment.html", context=context, request=request
    )
    file_name = (
        f"Monthly Expense order by {order_by} - {monthly_journal.created_at.date()}.pdf"
    )

    # Generate PDF
    html = HTML(string=html_content, base_url=request.build_absolute_uri("/"))
    pdf_file = html.write_pdf()
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{file_name}"'

    return response
