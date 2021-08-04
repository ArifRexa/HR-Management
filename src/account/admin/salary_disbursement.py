from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms.models import ModelChoiceIteratorValue

from account.models import SalaryDisbursement
from employee.models import Employee


class CustomFilteredSelect(FilteredSelectMultiple):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option_dict = super(CustomFilteredSelect, self).create_option(name, value, label, selected, index,
                                                                      subindex=None, attrs=None)

        value = ModelChoiceIteratorValue(value, instance=name)
        employee = Employee.objects.get(pk=value.__str__())
        option_dict['label'] = f'{label} | {employee.default_bank}'
        return option_dict


class SalaryDisbursementForm(forms.ModelForm):
    queryset = Employee.objects.filter(active=True, user__is_superuser=False).all()
    employee = forms.ModelMultipleChoiceField(
        queryset=queryset,
        widget=CustomFilteredSelect(verbose_name='employee', is_stacked=False),
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
