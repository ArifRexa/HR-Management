from copy import deepcopy

from django.contrib import admin
from django.db.models import QuerySet
from django.template.loader import get_template

import config.settings
from account.models import InvoiceDetail, Invoice
from config.utils.pdf import PDF


class InvoiceDetailsAdminInline(admin.StackedInline):
    model = InvoiceDetail
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('serial_no', 'date_time', 'client')
    actions = ('print_invoices', 'clone_invoice')
    inlines = (InvoiceDetailsAdminInline,)

    def clone_invoice(self, request, queryset: QuerySet(Invoice)):
        for invoice in queryset:
            invoice_details = invoice.invoicedetail_set.all()
            print(invoice_details)
            _invoice = invoice
            _invoice.pk = None
            _invoice.serial_no = invoice.serial_no + 1
            _invoice.save()
            for invoice_detail in invoice_details:
                _invoice_detail = invoice_detail
                _invoice_detail.pk = None
                _invoice_detail.save()

    def print_invoices(self, request, queryset):
        pdf = PDF()
        pdf.file_name = f'Invoice'
        pdf.template_path = "compliance/invoice.html"
        pdf.context = {
            'invoices': queryset,
            'seal': f"{config.settings.STATIC_ROOT}/stationary/sign_md.png"
        }
        return pdf.render_to_pdf(download=True)

    def has_module_permission(self, request):
        return False
