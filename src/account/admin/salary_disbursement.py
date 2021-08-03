from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from account.models import SalaryDisbursement
from employee.models import Employee


class SalaryDisbursementForm(forms.ModelForm):
    queryset = Employee.objects.filter(active=True).all()
    employee = forms.ModelMultipleChoiceField(
        queryset=queryset,
        widget=FilteredSelectMultiple(verbose_name='employee', is_stacked=False)
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
