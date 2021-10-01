from django.contrib import admin
from django.template.loader import get_template

from account.models import Loan, LoanPayment, LoanGuarantor, LoanAttachment
from config.utils.pdf import PDF


class LoadGuarantorInline(admin.StackedInline):
    model = LoanGuarantor
    extra = 1


class LoadAttachmentInline(admin.TabularInline):
    model = LoanAttachment
    extra = 0


@admin.register(Loan)
class LoadAdmin(admin.ModelAdmin):
    list_display = ('employee', 'loan_amount', 'emi', 'tenor')
    inlines = (LoadGuarantorInline, LoadAttachmentInline)
    actions = ('print_loan_agreement',)

    @admin.action(description='Print Agreement')
    def print_loan_agreement(self, request, queryset):
        pdf = PDF()
        pdf.file_name = f'Loan Agreement'
        pdf.template_path = 'agreements/loan_agreement.html'
        pdf.context = {'loans': queryset}
        return pdf.render_to_pdf(download=True)


@admin.register(LoanPayment)
class LoanPaymentAdmin(admin.ModelAdmin):
    list_display = ('loan', 'payment_amount')
