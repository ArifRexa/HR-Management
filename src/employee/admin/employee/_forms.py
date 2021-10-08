from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple, AdminDateWidget

from employee.models import Employee


class SMSAnnounceForm(forms.Form):
    employee_choice = Employee.objects.filter(active=True).all()
    message = forms.CharField(widget=forms.Textarea)
    employees = forms.ModelMultipleChoiceField(
        queryset=employee_choice,
        widget=FilteredSelectMultiple(verbose_name='employees', is_stacked=False)
    )

    class Media:
        css = {'all': ['admin/css/widgets.css']}
        js = ['/admin/jsi18n/']


class FilterForm(forms.Form):
    project_hour__date__gte = forms.DateField(label='', widget=AdminDateWidget(attrs={'readonly': 'readonly'}))
    project_hour__date__lte = forms.DateField(label=' ', widget=AdminDateWidget(attrs={'readonly': 'readonly'}))
