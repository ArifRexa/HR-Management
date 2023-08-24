from django.contrib import admin
from employee.models.excuse_note import ExcuseNote, ExcuseNoteAttachment, HRReportNoteCategory
from django.template.loader import get_template
from django.utils.html import format_html




class ExcuseNoteAttachmentInline(admin.TabularInline):
    model = ExcuseNoteAttachment
    extra = 0


@admin.register(ExcuseNote)
class ExcuseNoteAdmin(admin.ModelAdmin):
    list_display = ('get_date', 'category', 'employee', 'get_short_excuse_acts')
    list_filter = ('employee', 'category',)
    date_hierarchy = 'created_at'
    list_per_page = 20
    inlines = (ExcuseNoteAttachmentInline,)
    # autocomplete_fields = ['employee']


    class Media:
        css = {
            'all': ('css/list.css',)
        }
        js = ('js/list.js',)


    @admin.display(description="Date", ordering='created_at')
    def get_date(self, obj):
        return obj.created_at

    
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


@admin.register(HRReportNoteCategory)
class HRReportNoteCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'active',)

