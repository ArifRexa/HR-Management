import calendar
from datetime import datetime
from django.contrib import admin
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives


from account.models import (
    Loan,
    LoanPayment,
    LoanGuarantor,
    LoanAttachment,
    SalaryEmiLoan,
)
from config.utils.pdf import PDF
from django.contrib import messages
from django.db import models


class LoadGuarantorInline(admin.StackedInline):
    model = LoanGuarantor
    extra = 1


class LoadAttachmentInline(admin.TabularInline):
    model = LoanAttachment
    extra = 0


@admin.register(Loan)
class LoadAdmin(admin.ModelAdmin):
    list_display = ("employee", "loan_amount", "due", "emi", "tenor")
    inlines = (LoadAttachmentInline,)
    actions = ("print_loan_agreement", "duplicate")
    list_filter = (
        "loan_type",
        "employee",
    )
    search_fields = ("employee__full_name",)
    date_hierarchy = "effective_date"
    change_list_template = "admin/loan.html"

    @admin.action(description="Print Agreement")
    def print_loan_agreement(self, request, queryset):
        pdf = PDF()
        pdf.file_name = f"Loan Agreement"
        pdf.template_path = "agreements/loan_agreement.html"
        pdf.context = {"loans": queryset}
        return pdf.render_to_pdf(download=True)

    @admin.action(description="Duplicate selected items")
    def duplicate(self, request, queryset):
        for obj in queryset:
            obj.id = None
            obj.save()

        self.message_user(request, "Duplicated all selected items", messages.SUCCESS)

    @admin.display(description="Due amount")
    def due(self, obj: Loan):
        due_amount = (
            obj.loan_amount
            - obj.loanpayment_set.aggregate(
                total_payment=Coalesce(Sum("payment_amount"), 0.0)
            )["total_payment"]
        )
        return f"{due_amount} ({obj.loanpayment_set.count()})"

    def has_module_permission(self, request):
        if request.user.is_superuser or request.user.has_perm("account.add_loan"):
            return False
        elif request.user.has_perm("account.can_view_tax_loans"):
            return True
        return False

    def changelist_view(self, request, extra_context=None):
        # Ensure   extra_context is initialized as a dictionary if it's not passed
        extra_context = extra_context or {}

        # Get the response from the parent class's changelist_view
        response = super().changelist_view(request, extra_context=extra_context)

        try:
            # Get the queryset from the ChangeList
            cl = response.context_data["cl"]
            queryset = cl.queryset

            # Calculate the total loan amount
            total_loan = queryset.aggregate(total=models.Sum("emi"))["total"] or 0

            # Add the total loan amount to the extra context
            extra_context["total_loan"] = total_loan

            # Update the response context data with the new extra context
            response.context_data.update(extra_context)
        except (AttributeError, KeyError):
            pass  # If  the context or queryset doesn't exist, ignore

        return response

    def save_model(self, request, obj, form, change) -> None:
        html_template = get_template("mail/loan_mail.html")
        html_content = html_template.render({"loan": obj})

        email = EmailMultiAlternatives(subject=f"Loan Approved  ")
        email.attach_alternative(html_content, "text/html")
        email.to = [obj.employee.email]
        email.from_email = "admin@mediusware.com"
        email.send()
        return super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs
        elif request.user.has_perm("account.add_loan"):
            return qs
        elif request.user.has_perm("account.can_view_tax_loans"):
            return qs.filter(loan_type="tds")


@admin.register(LoanPayment)
class LoanPaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_date", "payment_amount", "loan", "note")
    date_hierarchy = "payment_date"
    list_filter = ("loan",)
    search_fields = ("loan__employee__full_name",)

    def has_module_permission(self, request):
        return False


@admin.register(SalaryEmiLoan)
class SalaryEmiLoanAdmin(admin.ModelAdmin):
    list_display = ("employee", "get_salary_loan")
    date_hierarchy = "created_at"
    change_list_template = "admin/salary_emi_loan.html"

    def get_salary_loan(self, obj):
        salary_date = obj.salary_sheet.date
        salary_month_start = datetime(salary_date.year, salary_date.month, 1).date()
        salary_month_end = datetime(
            salary_date.year,
            salary_date.month,
            calendar.monthrange(salary_date.year, salary_date.month)[1],
        ).date()

        loan_amount = obj.employee.loan_set.filter(
            start_date__lte=salary_month_end,
            end_date__gte=salary_month_start,
            loan_type="salary",
        )
        loan_amount = loan_amount.aggregate(Sum("emi"))
        return int(loan_amount["emi__sum"]) if loan_amount["emi__sum"] else 0

    get_salary_loan.short_description = "Salary Loan"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.filter(
            employee__loan__loan_type="salary",  # Only salary loans
            employee__loan__emi__gt=0,  # EMI greater than 0
        )
        a = []
        for obj in qs:
            salary_date = obj.salary_sheet.date
            salary_month_start = datetime(salary_date.year, salary_date.month, 1).date()
            salary_month_end = datetime(
                salary_date.year,
                salary_date.month,
                calendar.monthrange(salary_date.year, salary_date.month)[1],
            ).date()

            loan_amount = obj.employee.loan_set.filter(
                start_date__lte=salary_month_end,
                end_date__gte=salary_month_start,
                loan_type="salary",
            )
            if loan_amount.exists():
                a.append(obj.id)
        return qs.filter(id__in=a).distinct()

    def changelist_view(self, request, extra_context=None):
        res = super().changelist_view(request, extra_context)
        context = extra_context or {}
        cl = res.context_data["cl"]
        queryset = cl.queryset
        context["total_loan"] = (
            queryset.aggregate(total=models.Sum("employee__loan__emi"))["total"] or 0
        )
        res.context_data.update(context)

        return res

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=...):
        return False
