from django import forms

from employee.models.employee_activity import EmployeeProject
from datetime import datetime, timedelta, time
from django.core.exceptions import ValidationError
from django.utils import timezone


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
        fields = ["project_name", "start_time"]
        widgets = {
            # 'manager_or_lead': forms.Select(attrs={'class': 'form-select', 'style': 'height: 40px;'}),
            "project_name": forms.Select(
                attrs={
                    "class": "form-select",
                    "style": "height: 40px;",
                    "data-live-search": "true",
                }
            ),
            "start_time": forms.Select(
                attrs={"class": "form-select", "style": "height: 40px;"}
            ),
            # 'end_time': forms.Select(attrs={'class': 'form-select', 'style': 'height: 40px;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_time = timezone.now().time()
        booked_times = BookConferenceRoom.objects.filter(
            created_at__date=timezone.now().date()
        ).values_list(
            "start_time",
            flat=True,
        )
        # Filter out booked times from TIME_CHOICES
        available_choices = [
            choice
            for choice in BookConferenceRoom.TIME_CHOICES
            if choice[0] > current_time and choice[0] not in booked_times
        ]
        self.fields["start_time"].choices = available_choices
