from django import forms

from employee.models import EmployeeOnline


class EmployeeStatusForm(forms.ModelForm):
    class Meta:
        model = EmployeeOnline
        fields = ['active']
