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
    list_display = ('get_date', 'employee', 'category', 'severity', 'status', "get_short_excuse_acts")
    search_fields = ('employee__full_name', 'category__title', 'excuse_acts', 'status')
    list_filter = ('status', 'severity', 'category', 'employee' )
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

    
    @admin.display(description="Excuse/Acts")
    def get_short_excuse_acts(self, obj):
        html_template = get_template('admin/excuse_note/col_excuse_note.html')
        html_content = html_template.render({
            'excuse_acts': obj.excuse_acts,
            'action_taken': obj.action_taken if obj.action_taken else None,
        })
        return format_html(html_content)
    


    def save_model(self, request, obj, form, change):
        if not change:
            obj.reported_by = request.user.employee
        super().save_model(request, obj, form, change)
    
    @admin.action(description="Export selected reports to PDF")
    def export_to_pdf(self, request, queryset):
        if not queryset.exists():
            self.message_user(request, "No reports selected.", level='error')
            return
            
        # Prefetch related attachments to optimize queries
        queryset = queryset.order_by('created_at').prefetch_related('excusenoteattachment_set')
        note_ids = queryset.values_list('id', flat=True)
        id_str = "_".join(list(map(str, note_ids)))
        
        pdf = PDF()
        pdf.file_name = f"HR_Report_Notes-{id_str}"
        pdf.template_path = "compliance/hr_report_notes.html"
        protocol = "https" if request.is_secure() else "http"
        
        # Prepare context with additional attachment information
        pdf.context = {
            "notes": queryset,
            "host": f"{protocol}://{request.get_host()}",
            "include_attachments": True,  # Flag to control attachment display in template
        }
        
        return pdf.render_to_pdf(download=True)


@admin.register(HRReportNoteCategory)
class HRReportNoteCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'active',)
    search_fields = ('title',)

    def has_module_permission(self, request):
        return False

