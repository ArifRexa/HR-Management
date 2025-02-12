from django import forms

from client_management.models import ClientMeeting
from django.utils import timezone


class ClientMeetingForm(forms.ModelForm):

    class Meta:
        model = ClientMeeting
        fields = ("project", "start_time")
        widgets = {
            "project": forms.Select(
                attrs={
                    "class": "form-select",
                    "style": "height: 40px;",
                    "data-live-search": "true",
                }
            ),
            "start_time": forms.DateTimeInput(attrs={'type': 'datetime-local', "class": "form-control"}),
        }
        

    def clean(self):
        if ClientMeeting.objects.filter(
            project=self.cleaned_data.get("project"),
            start_time=self.cleaned_data.get("start_time"),
        ).exists():
            raise forms.ValidationError("Already Schedule Meeting For This Time")
        if self.cleaned_data["start_time"] < timezone.now():
            raise forms.ValidationError("Start time cannot be in the past")
        return super().clean()