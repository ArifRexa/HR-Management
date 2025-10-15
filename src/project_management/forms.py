from django import forms
from django.forms import BaseInlineFormSet
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.contrib.admin.widgets import AdminDateWidget
from project_management.models import DailyProjectUpdate


# class ClientFeedbackForm(forms.ModelForm):
#     class Meta:
#         model = ClientFeedback
#         fields = [
#             "feedback",
#             "rating_communication",
#             "rating_output",
#             "rating_time_management",
#             "rating_billing",
#             "rating_long_term_interest",
#         ]
#         labels = {
#             "rating_communication": "Communication",
#             "rating_output": "Output",
#             "rating_time_management": "Time Management",
#             "rating_billing": "Billing",
#             "rating_long_term_interest": "Long-Term Working Interest",
#         }

# class ClientFeedbackForm(forms.ModelForm):

#     class Meta:
#         model = ClientFeedback
#         fields = [
#             "feedback",
#             "rating_communication",
#             "rating_overall_satisfaction",
#             "rating_quality_of_work",
#             "rating_time_management",
#             "rating_value_for_money",
#             "rating_understanding_of_requirements",
#             "rating_recommendations",
#         ]
#         labels = {
#             "rating_communication": "Communication",
#             "rating_overall_satisfaction": "Overall Satisfaction",
#             "rating_quality_of_work": "Quality of Work",
#             "rating_time_management": "Time Management",
#             "rating_value_for_money": "Value for Money",
#             "rating_understanding_of_requirements": "Understanding of Requirements",
#             "rating_recommendations": "Recommendations",
#         }


class AddDDailyProjectUpdateForm(forms.ModelForm):
    # key = forms.CharField(max_length=50, required=False)
    # value = forms.CharField(max_length=255, required=False)

    class Meta:
        model = DailyProjectUpdate
        fields = "__all__"  # Include all fields or specify the fields you want
        widgets = {
            "management_updates": forms.Textarea(
                attrs={"class": "cs-form-control-text"}
            )
        }

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

class ProjectHourFilterForm(forms.Form):
    created_at__date__gte = forms.DateField(label='From', widget=AdminDateWidget(attrs={'type':'date'}))
    created_at__date__lte = forms.DateField(label='To', widget=AdminDateWidget(attrs={'type':'date'}))