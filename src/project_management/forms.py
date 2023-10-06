from django import forms
from django.forms import BaseInlineFormSet

from project_management.models import ClientFeedback, DailyProjectUpdate


class ClientFeedbackForm(forms.ModelForm):
    class Meta:
        model = ClientFeedback
        fields = [
            'feedback',
            'rating_communication',
            'rating_output',
            'rating_time_management',
            'rating_billing',
            'rating_long_term_interest',
        ]
        labels = {
            'rating_communication': 'Communication',
            'rating_output': 'Output',
            'rating_time_management': 'Time Management',
            'rating_billing': 'Billing',
            'rating_long_term_interest': 'Long-Term Working Interest',
        }


class AddDDailyProjectUpdateForm(forms.ModelForm):
    key = forms.CharField(max_length=50, required=False)
    value = forms.CharField(max_length=255, required=False)

    class Meta:
        model = DailyProjectUpdate
        fields = '__all__'  # Include all fields or specify the fields you want

    # Customize form fields here

