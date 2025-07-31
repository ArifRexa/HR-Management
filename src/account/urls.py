from django.urls import path

from account.views import (
    account_journal,
    balance_sheet,
    costs_by_expense_group,
    journal_voucher,
    monthly_expense_attachment,
    monthly_expense_statement,
    payment_voucher,
)

app_name = "account"

urlpatterns = [
    path("payment-voucher/<int:id>/", payment_voucher, name="payment_voucher"),
    path("journal-voucher/<int:id>/", journal_voucher, name="journal_voucher"),
    path("account-journal/<int:id>/", account_journal, name="account_journal"),
    path("group-expenses-costs/<int:id>/", costs_by_expense_group, name="group_costs"),
    path("balance_sheet/<int:id>/", balance_sheet, name="balance_sheet"),
    path(
        "monthly-expense/<int:id>/", monthly_expense_statement, name="monthly_expense"
    ),
    path(
        "monthly-expense-attachment/<int:id>/",
        monthly_expense_attachment,
        name="monthly_expense_attachment",
    ),
]
