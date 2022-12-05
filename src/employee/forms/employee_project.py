from django import forms

from employee.models.employee_activity import EmployeeProject


class EmployeeProjectForm(forms.ModelForm):
    class Meta:
        model = EmployeeProject
        fields = ['project']
