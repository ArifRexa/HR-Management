import calendar
from datetime import date, datetime
from django.contrib import admin
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

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
    list_display = ("employee", "loan_amount", "due", "emi", "tenor", "description")
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

        email = EmailMultiAlternatives(subject="Loan Approved")
        email.attach_alternative(html_content, "text/html")
        email.to = [obj.employee.email]
        email.from_email = "hr@mediusware.com"
        email.cc = ["admin@mediusware.com"]
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
    autocomplete_fields = ("loan", )

    def has_module_permission(self, request):
        return False


@admin.register(SalaryEmiLoan)
class SalaryEmiLoanAdmin(admin.ModelAdmin):
    list_display = ("employee", "get_salary_loan")
    date_hierarchy = "salary_sheet__date"
    change_list_template = "admin/salary_emi_loan.html"

    def get_salary_loan(self, obj):
        return int(obj.salary_loan) if obj.salary_loan else 0

    get_salary_loan.short_description = "Salary Loan"

    def get_queryset(self, request):
        from django.db.models import Sum, OuterRef, Subquery, F, DateField
        from django.db.models.functions import TruncMonth
        from datetime import timedelta
        from django.db.models.expressions import ExpressionWrapper

        qs = super().get_queryset(request).select_related("employee", "salary_sheet")

        # Annotate the first day of the month for salary_sheet__date
        qs = qs.annotate(salary_month_start=TruncMonth("salary_sheet__date"))

        # Calculate the last day of the month by moving to the next month and subtracting one day
        qs = qs.annotate(
            salary_month_end=ExpressionWrapper(
                F("salary_month_start") + timedelta(days=31) - timedelta(days=1),
                output_field=DateField(),
            )
        )

        # Define a subquery to calculate total EMI for loans within the salary month range
        loan_emi_subquery = (
            Loan.objects.filter(
                employee=OuterRef("employee"),
                start_date__lte=OuterRef("salary_month_end"),
                end_date__gte=OuterRef("salary_month_start"),
                loan_type="salary",
            )
            .values("employee")
            .annotate(total_emi=Sum("emi"))
            .values("total_emi")
        )

        # Annotate the SalaryEmiLoan queryset with the total loan EMI
        qs = qs.annotate(salary_loan=Subquery(loan_emi_subquery)).filter(salary_loan__gt=0)

        return qs

    def changelist_view(self, request, extra_context=None):
        res = super().changelist_view(request, extra_context)
        context = extra_context or {}
        cl = res.context_data["cl"]
        queryset = cl.queryset
        context["total_loan"] = (
            queryset.aggregate(total=models.Sum("salary_loan"))["total"] or 0
        )
        res.context_data.update(context)

        return res

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=...):
        return False
