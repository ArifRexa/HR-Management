from django.contrib import admin
from django.template.loader import get_template
from django.utils.html import format_html
from employee.models import Skill, Learning, EmployeeExpertise, EmployeeExpertTech, EmployeeTechnology

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
    search_fields = ('name',)

    def get_fields(self, request, obj=None):
        if request.user.is_superuser or request.user.employee.manager:
            return ['name', 'icon', 'url', 'active']
        return ['name', 'icon', 'url']
#

    def save_model(self, request, obj, form, change):

        if change:
            obj.active = form.cleaned_data.get('active')
            expert = EmployeeExpertTech.objects.get(id=obj.id)
            if not form.cleaned_data.get('active'):
                expert.delete()
        super().save_model(request, obj, form, change)


@admin.register(EmployeeExpertTech)
class EmployeeExpertiseLevelAdmin(admin.ModelAdmin):
    list_display = ('level', )


class EmployeeExpertTechInlineAdmin(admin.TabularInline):

    model = EmployeeExpertTech
    extra = 0
    # autocomplete_fields = ('technology__name',)





@admin.register(EmployeeExpertise)
class EmployeeExpertiseAdmin(admin.ModelAdmin):
    list_display = ('employee', 'get_tech')
    search_fields = ('employee__full_name', 'employee_expertise__technology__name', 'employee_expertise__level')
    list_filter = ('employee_expertise__level', 'employee_expertise__technology__name', 'employee')
    autocomplete_fields = ('employee', )
    readonly_fields = ['employee']
    inlines = (EmployeeExpertTechInlineAdmin,)

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
        print()
        html_content = html_template.render({
            'obj': obj.employee_expertise.all()
        })

        return format_html(html_content)

    def save_model(self, request, obj, form, change):
        from django.shortcuts import redirect
        from django.contrib import messages
        if request.user.is_superuser:
            obj.employee = form.cleaned_data.get('employee')
        else:
            obj.employee = request.user.employee
        employee_expert = EmployeeExpertise.objects.filter(employee=obj.employee)
        if not change:
            if employee_expert.exists():
                obj.id = employee_expert[0].id
                messages.error(request, 'You have Expertise just add technology')
                return #self.message_user(request, 'You have Expertise just add technology')
        super().save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        print('hello world')
        from django.shortcuts import redirect
        if obj.pk:
            return super().response_add(
                request,
                obj,
                post_url_continue=post_url_continue
            )
        else:
            return redirect('/admin/employee/employeeexpertise/')
