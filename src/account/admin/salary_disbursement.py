from django import forms
from django.contrib import admin
from account.models import SalaryDisbursement
from config.widgets.mw_select_multiple import EmployeeFilteredSelectMultiple
from employee.models import Employee


class SalaryDisbursementForm(forms.ModelForm):
    queryset = Employee.objects.filter(active=True).all()
    employee = forms.ModelMultipleChoiceField(
        queryset=queryset,
        widget=EmployeeFilteredSelectMultiple(verbose_name='employee', is_stacked=False,
                                              aln_labels=['full_name', 'default_bank']),
    )

    class Meta:
        model = SalaryDisbursement
        fields = '__all__'


@admin.register(SalaryDisbursement)
class SalaryDisbursementAdmin(admin.ModelAdmin):
    list_display = ('title', 'disbursement_type', 'total_employee')
    form = SalaryDisbursementForm

    def total_employee(self, obj):
        return obj.employee.count()

    def has_module_permission(self, request):
        return False
