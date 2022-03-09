from django import forms
from django.contrib import admin
from django.utils.html import format_html

from config.widgets.mw_select_multiple import EmployeeFilteredSelectMultiple
from employee.models import Employee
from project_management.models import DurationUnit, ProjectResource


@admin.register(DurationUnit)
class DurationUnitAdmin(admin.ModelAdmin):
    pass


class ProjectResourceAdminForm(forms.ModelForm):
    queryset = Employee.objects.filter(active=True).all()
    employees = forms.ModelMultipleChoiceField(
        queryset=queryset,
        widget=EmployeeFilteredSelectMultiple(verbose_name='employee', is_stacked=False,
                                              aln_labels=[]),
    )

    class Meta:
        model = ProjectResource
        fields = '__all__'


@admin.register(ProjectResource)
class ProjectResourceAdmin(admin.ModelAdmin):
    list_display = ('project', 'get_duration', 'manager', 'get_employees', 'active')
    list_filter = ('project', 'manager')
    search_fields = ('project', 'manager')
    form = ProjectResourceAdminForm

    def save_model(self, request, obj, form, change):
        """
        override project hour save
        manager id will be authenticate user employee id if the user is not super user
        """
        if not obj.manager_id:
            obj.manager_id = request.user.employee.id
        super().save_model(request, obj, form, change)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request)
        if not request.user.is_superuser:
            fields.remove('manager')
        return fields

    @admin.display(description='Employees')
    def get_employees(self, obj: ProjectResource):
        employees = ''
        for employee in obj.employees.all():
            employees += format_html(f'{employee} <br>')
        return format_html(employees)

    @admin.display(description='Project Duration')
    def get_duration(self, obj: ProjectResource):
        return f'{obj.duration} {obj.duration_unit}'
