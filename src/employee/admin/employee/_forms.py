from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple, AdminDateWidget, AdminIntegerFieldWidget

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


class DateFilterForm(forms.Form):
    date__gte = forms.DateField(label='', widget=AdminDateWidget(attrs={'readonly': 'readonly'}))
    date__lte = forms.DateField(label='', widget=AdminDateWidget(attrs={'readonly': 'readonly'}))


class DailyUpdateFilterForm(forms.Form):
    created_at__date__gte = forms.DateField(label='From', widget=AdminDateWidget(attrs={'type':'date'}))
    created_at__date__lte = forms.DateField(label='To', widget=AdminDateWidget(attrs={'type':'date'}))


class DailyUpdateDateFilterForm(forms.Form):
    created_at__date = forms.DateField(
        label="Date",
        widget=AdminDateWidget(attrs={"readonly": "readonly"}),
    )
    total_hour__gte = forms.IntegerField(
        label="Hours (from)",
        min_value=0,
        required=False,
        widget=AdminIntegerFieldWidget(),
    )
    total_hour__lte = forms.IntegerField(
        label="Hours (to)",
        min_value=0,
        required=False,
        widget=AdminIntegerFieldWidget(),
    )


class DailyExpenseFilterForm(forms.Form):
    date__gte = forms.DateField(label='From', widget=AdminDateWidget(attrs={'type': 'date'}))
    date__lte = forms.DateField(label='To', widget=AdminDateWidget(attrs={'type': 'date'}))


class NOCIntermediateForm(forms.Form):
    noc_body = forms.CharField(label="NOC Body Text", widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        noc_body = kwargs.pop('noc_body', '')
        super().__init__(*args, **kwargs)
        self.fields["noc_body"].initial = noc_body

