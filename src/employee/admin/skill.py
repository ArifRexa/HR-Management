from django.contrib import admin
from django.template.loader import get_template
from django.utils.html import format_html
from employee.models import Skill, Learning, EmployeeTechnology, EmployeeExpertise

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

    def has_module_permission(self, request):
        return False


@admin.register(EmployeeTechnology)
class EmployeeTechAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'url')
    search_fields = ('name',)


@admin.register(EmployeeExpertise)
class EmployeeExpertise(admin.ModelAdmin):
    list_display = ('employee', 'get_tech', 'level', 'created_at')
    search_fields = ('employee__full_name', 'technology__name')
    list_filter = ('level', 'technology', 'employee')
    autocomplete_fields = ('technology', 'employee')
    readonly_fields = ['employee']

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ['employee', 'technology', 'level']
        return ['technology', 'level']

    def get_readonly_fields(self, request, obj=None):
        if not obj:
            return []
        if request.user.is_superuser:
            return []
        if obj and request.user.employee == obj.employee:
            return []
        return ['employee', 'technology', 'level']

    @admin.display(description="Skill")
    def get_tech(self, obj):
        return obj.technology.name

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            obj.employee = form.cleaned_data.get('employee')
        else:
            obj.employee = request.user.employee

        super().save_model(request, obj, form, change)
