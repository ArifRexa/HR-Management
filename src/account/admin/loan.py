from django.contrib import admin
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives

from account.models import Loan, LoanPayment, LoanGuarantor, LoanAttachment
from config.utils.pdf import PDF
from django.contrib import messages


class LoadGuarantorInline(admin.StackedInline):
    model = LoanGuarantor
    extra = 1


class LoadAttachmentInline(admin.TabularInline):
    model = LoanAttachment
    extra = 0


@admin.register(Loan)
class LoadAdmin(admin.ModelAdmin):
    list_display = ('employee', 'loan_amount', 'due', 'emi', 'tenor')
    inlines = (LoadGuarantorInline, LoadAttachmentInline)
    actions = ('print_loan_agreement', 'duplicate')
    list_filter = ('employee',)
    search_fields = ('employee__full_name',)
    date_hierarchy = 'created_at'

    @admin.action(description='Print Agreement')
    def print_loan_agreement(self, request, queryset):
        pdf = PDF()
        pdf.file_name = f'Loan Agreement'
        pdf.template_path = 'agreements/loan_agreement.html'
        pdf.context = {'loans': queryset}
        return pdf.render_to_pdf(download=True)
    
    @admin.action(description="Duplicate selected items")
    def duplicate(self, request, queryset):
        for obj in queryset:
            obj.id = None
            obj.save()

        self.message_user(request, 'Duplicated all selected items', messages.SUCCESS)
         

    @admin.display(description='Due amount')
    def due(self, obj: Loan):
        due_amount = obj.loan_amount - obj.loanpayment_set.aggregate(
            total_payment=Coalesce(Sum('payment_amount'), 0.0)
        )['total_payment']
        return f'{due_amount} ({obj.loanpayment_set.count()})'
    
    def has_module_permission(self, request):
        return False

    def save_model(self, request, obj, form, change) -> None:
        html_template = get_template('mail/loan_mail.html')
        html_content = html_template.render({
            'loan': obj
        })

        email = EmailMultiAlternatives(subject=f'Loan Approved  ')
        email.attach_alternative(html_content, 'text/html')
        email.to = [obj.employee.email]
        email.from_email = 'admin@mediusware.com'
        # email.send()

        return super().save_model(request, obj, form, change)


@admin.register(LoanPayment)
class LoanPaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_date', 'payment_amount', 'loan', 'note')
    date_hierarchy = 'payment_date'
    list_filter = ('loan',)
    search_fields = ('loan__employee__full_name',)

    def has_module_permission(self, request):
        return False
