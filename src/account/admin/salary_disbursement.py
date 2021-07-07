from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Value, CharField
from django.db.models.functions import Concat

from account.models import SalaryDisbursement
from employee.models import Employee


def get_choices(instance):
    return 'ok'


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
    list_display = ('title', 'disbursement_type')
    form = SalaryDisbursementForm
