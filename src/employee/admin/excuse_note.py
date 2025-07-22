from django.contrib import admin
from config import settings
from config.utils.pdf import PDF
from employee.models.excuse_note import ExcuseNote, ExcuseNoteAttachment, HRReportNoteCategory
from django.template.loader import get_template
from django.utils.html import format_html
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from reportlab.lib.units import inch


class ExcuseNoteAttachmentInline(admin.TabularInline):
    model = ExcuseNoteAttachment
    extra = 0


@admin.register(ExcuseNote)
class ExcuseNoteAdmin(admin.ModelAdmin):
    list_display = ('get_date', 'employee', 'category', 'severity', 'status')
    search_fields = ('employee__full_name', 'category__title', 'excuse_acts', 'status')
    list_filter = ('employee', 'category', 'severity', 'status', 'category')
    date_hierarchy = 'created_at'
    list_per_page = 20
    inlines = (ExcuseNoteAttachmentInline,)
    autocomplete_fields = ('employee', 'category',)
    readonly_fields = ('reported_by', 'created_at', 'updated_at')
    # exclude = ('created_at', 'updated_at')
    actions = ['export_to_pdf']

    class Media:
        css = {
            'all': ('css/list.css',)
        }
        js = ('js/list.js',)


    @admin.display(description="Date", ordering='created_at')
    def get_date(self, obj):
        return obj.incedent_date
        # return obj.created_at

    
    @admin.display(description="Excuse/Acts:")
    def get_short_excuse_acts(self, obj):
        html_template = get_template('admin/excuse_note/col_excuse_note.html')
        html_content = html_template.render({
            'excuse_acts': obj.excuse_acts,
        })
        return format_html(html_content)
    

    def has_module_permission(self, request): 
        return super().has_module_permission(request)
        # return False

    def save_model(self, request, obj, form, change):
        # Set reported_by to the current user when creating a new object
        if not change:  # Only for creation, not updates
            obj.reported_by = request.user.employee
        super().save_model(request, obj, form, change)

    
    # @admin.action(description="Export selected reports to PDF")
    # def export_to_pdf(self, request, queryset):
    #     # Check if any records are selected
    #     if not queryset.exists():
    #         self.message_user(request, "No reports selected.", level='error')
    #         return

    #     # Create a BytesIO buffer to hold the PDF
    #     buffer = BytesIO()

    #     # Create the PDF document
    #     doc = SimpleDocTemplate(
    #         buffer,
    #         pagesize=letter,
    #         leftMargin=0.75*inch,
    #         rightMargin=0.75*inch,
    #         topMargin=0.75*inch,
    #         bottomMargin=0.75*inch
    #     )
    #     elements = []

    #     # Define styles for the PDF
    #     styles = getSampleStyleSheet()
    #     title_style = styles['Heading1']
    #     heading_style = styles['Heading3']
    #     normal_style = styles['Normal']
    #     normal_style.fontSize = 10
    #     normal_style.leading = 12  # Line spacing for readability
    #     normal_style.wordWrap = 'CJK'  # Better wrapping for long text

    #     # Add a title to the PDF
    #     elements.append(Paragraph("HR Report Notes", title_style))
    #     elements.append(Spacer(1, 0.05*inch))

    #     # Add each ExcuseNote record
    #     for index, note in enumerate(queryset, 1):
    #         # Add a separator for multiple records
    #         if index > 1:
    #             elements.append(Spacer(1, 0.05*inch))
    #             elements.append(Paragraph(f"{'-'*40}", normal_style))
    #             elements.append(Spacer(1, 0.05*inch))

    #         # Incident Date
    #         elements.append(Paragraph("Incident Date", heading_style))
    #         elements.append(Paragraph(
    #             note.incedent_date.strftime('%Y-%m-%d') if note.incedent_date else 'N/A',
    #             normal_style
    #         ))
    #         elements.append(Spacer(1, 0.1*inch))

    #         # Reported By and Severity (combined, labels bold, values normal)
    #         reported_by = str(note.reported_by) if note.reported_by else 'N/A'
    #         elements.append(Paragraph(
    #             f"<b>Reported By:</b> {reported_by}  |  <b>Severity:</b> {note.get_severity_display()}",
    #             normal_style
    #         ))
    #         elements.append(Spacer(1, 0.1*inch))

    #         # Category and Status (combined, labels bold, values normal)
    #         elements.append(Paragraph(
    #             f"<b>Category:</b> {str(note.category)}  |  <b>Status:</b> {note.get_status_display()}",
    #             normal_style
    #         ))
    #         elements.append(Spacer(1, 0.1*inch))

    #         # Employee
    #         elements.append(Paragraph("Employee", heading_style))
    #         elements.append(Paragraph(str(note.employee), normal_style))
    #         elements.append(Spacer(1, 0.1*inch))

    #         # Excuse Acts
    #         elements.append(Paragraph("Excuse Acts", heading_style))
    #         elements.append(Paragraph(note.excuse_acts or 'N/A', normal_style))
    #         elements.append(Spacer(1, 0.1*inch))

    #         # Action Taken
    #         elements.append(Paragraph("Action Taken", heading_style))
    #         elements.append(Paragraph(note.action_taken or 'N/A', normal_style))
    #         elements.append(Spacer(1, 0.1*inch))

    #     # Build the PDF
    #     doc.build(elements)

    #     # Get the PDF data from the buffer
    #     pdf = buffer.getvalue()
    #     buffer.close()

    #     # Create the HTTP response with the PDF
    #     response = HttpResponse(content_type='application/pdf')
    #     response['Content-Disposition'] = 'attachment; filename="hr_report_notes.pdf"'
    #     response.write(pdf)

    #     return response
    @admin.action(description="Export selected reports to PDF")
    def export_to_pdf(self, request, queryset):
        # Check if any records are selected
        if not queryset.exists():
            self.message_user(request, "No reports selected.", level='error')
            return

        # Order queryset by created_at
        queryset = queryset.order_by('created_at')
        note_ids = queryset.values_list('id', flat=True)
        id_str = "_".join(list(map(str, note_ids)))

        # Initialize PDF object
        pdf = PDF()
        pdf.file_name = f"HR_Report_Notes-{id_str}"
        pdf.template_path = "compliance/hr_report_notes.html"
        protocol = "https" if request.is_secure() else "http"

        # Prepare context for the template
        pdf.context = {
            "notes": queryset,
            "host": f"{protocol}://{request.get_host()}"
        }
        # Render and return the PDF
        return pdf.render_to_pdf(download=True)


@admin.register(HRReportNoteCategory)
class HRReportNoteCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'active',)
    search_fields = ('title',)

    def has_module_permission(self, request):
        return False

