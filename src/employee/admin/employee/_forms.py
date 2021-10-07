from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from employee.models import Employee


class SMSAnnounceForm(forms.Form):
    employee_choice = Employee.objects.filter(active=True).values_list('id', 'full_name')
    message = forms.CharField(widget=forms.Textarea)
    employees = forms.MultipleChoiceField(widget=FilteredSelectMultiple(verbose_name='employee', is_stacked=False),
                                          choices=employee_choice)

    class Media:
        css = {'all': ['admin/css/widgets.css']}
        js = ['/admin/jsi18n/']
