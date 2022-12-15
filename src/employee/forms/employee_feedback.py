from django import forms

from employee.models import EmployeeFeedback


class EmployeeFeedbackForm(forms.ModelForm):
    class Meta:
        model = EmployeeFeedback
        fields = ['feedback', 'rating']
