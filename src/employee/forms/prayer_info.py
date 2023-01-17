from django import forms

from employee.models import PrayerInfo

class EmployeePrayerInfoForm(forms.ModelForm):
    class Meta:
        model = PrayerInfo
        fields = ['num_of_waqt']
        labels = {
            "num_of_waqt": "Prayers Today"
        }
