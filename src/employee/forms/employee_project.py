from django import forms

from employee.models.employee_activity import EmployeeProject
from datetime import datetime, timedelta, time
from django.core.exceptions import ValidationError


class EmployeeProjectForm(forms.ModelForm):
    class Meta:
        model = EmployeeProject
        fields = ["project"]

    def __init__(self, *args, **kwargs):
        super(EmployeeProjectForm, self).__init__(*args, **kwargs)
        self.fields["project"].widget.attrs.update({"hidden": "hidden"})

from employee.models import BookConferenceRoom, Employee

class BookConferenceRoomForm(forms.ModelForm):
    class Meta:
        model = BookConferenceRoom
        fields = ['project_name', 'start_time']
        widgets = {
            # 'manager_or_lead': forms.Select(attrs={'class': 'form-select', 'style': 'height: 40px;'}),
            'project_name': forms.Select(attrs={'class': 'form-select', 'style': 'height: 40px;'}),
            'start_time': forms.Select(attrs={'class': 'form-select', 'style': 'height: 40px;'}),
            # 'end_time': forms.Select(attrs={'class': 'form-select', 'style': 'height: 40px;'}),
        }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['manager_or_lead'].queryset = Employee.objects.filter(manager=True) | Employee.objects.filter(lead=True)
    
