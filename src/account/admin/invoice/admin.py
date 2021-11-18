from django.contrib import admin
from django.template.loader import get_template

from account.models import InvoiceDetail, Invoice
from config.utils.pdf import PDF


class InvoiceDetailsAdminInline(admin.StackedInline):
    model = InvoiceDetail
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('serial_no', 'date_time', 'client')
    actions = ('print_invoices',)
    inlines = (InvoiceDetailsAdminInline,)

    def print_invoices(self, request, queryset):
        pdf = PDF()
        pdf.file_name = f'Invoice'
        pdf.template_path = "compliance/invoice.html"
        pdf.context = {'invoices': queryset}
        return pdf.render_to_pdf(download=False)
