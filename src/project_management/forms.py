from django import forms

from project_management.models import ClientFeedback


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
