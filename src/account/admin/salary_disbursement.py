from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from account.models import SalaryDisbursement
from employee.models import Employee


class SalaryDisbursementForm(forms.ModelForm):
    employee = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(active=True).all(),
        widget=FilteredSelectMultiple("employee", is_stacked=False)
    )

    class Meta:
        model = SalaryDisbursement
        fields = '__all__'


@admin.register(SalaryDisbursement)
class SalaryDisbursementAdmin(admin.ModelAdmin):
    list_display = ('title', 'disbursement_type')
    form = SalaryDisbursementForm
