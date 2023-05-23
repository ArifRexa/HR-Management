from django.contrib import admin
from django.template.loader import get_template
from django.utils.html import format_html
from employee.models import Skill, Learning


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'note')
    search_fields = ('title',)
    list_per_page = 20

    def has_module_permission(self, request):
        return False


@admin.register(Learning)
class LearningAdmin(admin.ModelAdmin):
    list_display = ('asigned_to', 'asigned_by', 'get_details', 'created_at')
    search_fields = ('details', 'asigned_by__full_name', 'asigned_to__full_name')
    # autocomplete_fields = ['asigned_by', 'asigned_to']
    list_per_page = 30

    class Media:
        css = {
            'all': ('css/list.css',)
        }
        js = ('js/list.js',)

    @admin.display(description="details")
    def get_details(self, obj):
        html_template = get_template(
            'admin/employee/list/col_learning.html'
        )
        html_content = html_template.render({
            'details': obj.details.replace('{', '_').replace('}', '_'),
        })

        try:
            data = format_html(html_content)
        except:
            data = "-"

        return data
