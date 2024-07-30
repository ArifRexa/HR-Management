from django import forms
from django.forms import BaseInlineFormSet
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from project_management.models import ClientFeedback, DailyProjectUpdate


class ClientFeedbackForm(forms.ModelForm):
    class Meta:
        model = ClientFeedback
        fields = [
            "feedback",
            "rating_communication",
            "rating_output",
            "rating_time_management",
            "rating_billing",
            "rating_long_term_interest",
        ]
        labels = {
            "rating_communication": "Communication",
            "rating_output": "Output",
            "rating_time_management": "Time Management",
            "rating_billing": "Billing",
            "rating_long_term_interest": "Long-Term Working Interest",
        }


class AddDDailyProjectUpdateForm(forms.ModelForm):
    # key = forms.CharField(max_length=50, required=False)
    # value = forms.CharField(max_length=255, required=False)

    class Meta:
        model = DailyProjectUpdate
        fields = "__all__"  # Include all fields or specify the fields you want

    # Customize form fields here
    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(AddDDailyProjectUpdateForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        # self.fields['hours'].required = False

    def is_valid_url(self, url):
        validator = URLValidator()
        try:
            validator(url.strip())
            return True
        except ValidationError:
            return False

    # def clean(self):
    #     cleaned_data = super().clean()

    #     update_json = cleaned_data.get("updates_json")

    #     for item in update_json:
    #         link = item[2]
    #         if link == "":
    #             raise forms.ValidationError(
    #                 {"updates_json":"Please enter a commit link"},
    #             )
    #         if not self.is_valid_url(link):
    #             raise forms.ValidationError(
    #                 {"updates_json":"Please enter a valid URL"},
    #             )
    #     return cleaned_data
