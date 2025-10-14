from django.contrib import admin
from django.template.loader import get_template
from django.utils.html import format_html
from employee.models import Skill, Learning, EmployeeExpertise, EmployeeTechnology

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
class EmployeeTechnologyAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'url', 'active')
    list_filter = ('active', 'name')
    search_fields = ('name',)
    actions = ('approve_selected',)

    def get_fields(self, request, obj=None):
        if request.user.is_superuser or request.user.employee.manager:
            return ['name', 'icon', 'url', 'active']
        return ['name', 'icon', 'url']

    @admin.action()
    def active_selected(self, request, queryset):
        if request.user.is_superuser or request.user.employee.manager or request.user.employee.lead:
            queryset.update(active=True)

    def get_actions(self, request):
        action = super().get_actions(request)
        if request.user.is_superuser or request.user.employee.manager or request.user.employee.lead:
            action['Active all selected'] = (
                self.active_selected,
                'Active all selected',
                'Active all selected'
            )
            action['Inactive all selected'] = (
                self.inactive_selected,
                'Inactive all selected',
                'Inactive all selected'
            )
        return action

    @admin.action()
    def inactive_selected(self, request, queryset):
        if request.user.is_superuser or request.user.employee.manager or request.user.employee.lead:
            queryset.update(active=True)

    # def save_model(self, request, obj, form, change):

    #     if change:
    #         obj.active = form.cleaned_data.get('active')
    #         if EmployeeExpertTech.objects.filter(technology=obj).exists():
    #             expert = EmployeeExpertTech.objects.get(technology=obj)
    #             if not form.cleaned_data.get('active'):
    #                 expert.delete()
    #     super().save_model(request, obj, form, change)


# @admin.register(EmployeeExpertTech)
# class EmployeeExpertiseLevelAdmin(admin.ModelAdmin):
#     list_display = ('technology', 'get_employee', 'level', 'percentage', 'get_active')
#     search_fields = ('technology__name', 'level', 'employee_expertise__employee__full_name')
#     list_filter = ('level', 'technology__name',  'employee_expertise__employee__full_name')

#     @admin.display(description="Employee")
#     def get_employee(self, obj):
#         return obj.employee_expertise.employee.full_name

#     @admin.display(description='Active')
#     def get_active(self, obj):
#         return '\u2705' if obj.technology.active else '\u274C'


# class EmployeeExpertTechInlineAdmin(admin.TabularInline):

#     model = EmployeeExpertTech
#     extra = 0
#     autocomplete_fields = ('technology',)

#     def get_readonly_fields(self, request, obj=None):
#         if not obj:
#             return []
#         if request.user.employee == obj.employee or request.user.is_superuser:
#             return []
#         return ['technology', 'level', 'percentage']

#     def has_add_permission(self, request, obj):
#         if not obj:
#             return True
#         if request.user.employee == obj.employee or request.user.is_superuser:
#             return True
#         return False

#     def has_delete_permission(self, request, obj=None):
#         if not obj:
#             return True
#         if request.user.employee == obj.employee or request.user.is_superuser:
#             return True
#         return False


@admin.register(EmployeeExpertise)
class EmployeeExpertiseAdmin(admin.ModelAdmin):
    list_display = ('employee', 'get_tech')
    search_fields = ('employee__full_name', 'employee_expertise__level')
    list_filter = ('employee',)
    autocomplete_fields = ('employee', )
    readonly_fields = ['employee']
    # inlines = (EmployeeExpertTechInlineAdmin,)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        if not obj and request.user.is_superuser:
            return []
        if obj and request.user.employee == obj.employee:
            return ['employee']
        return self.readonly_fields

    @admin.display(description="Expertise")
    def get_tech(self, obj):
        html_template = get_template('admin/col_expertise.html')
        html_content = html_template.render({
            'obj': obj.employee_expertise.all()
        })

        return format_html(html_content)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        if EmployeeExpertise.objects.filter(employee=request.user.employee).exists():
            return False
        return True

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            obj.employee = form.cleaned_data.get('employee')
        else:
            obj.employee = request.user.employee

        super().save_model(request, obj, form, change)

