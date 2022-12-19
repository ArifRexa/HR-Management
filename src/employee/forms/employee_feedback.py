from django import forms

from employee.models import EmployeeFeedback


class EmployeeFeedbackForm(forms.ModelForm):
    class Meta:
        model = EmployeeFeedback
        fields = [
            'feedback', 
            'environmental_rating', 
            'facilities_rating', 
            'learning_growing_rating', 
            'happiness_index_rating', 
            'boss_rating'
        ]
