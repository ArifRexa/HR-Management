from django import forms

from employee.models import PrayerInfo

class EmployeePrayerInfoForm(forms.ModelForm):
    class Meta:
        model = PrayerInfo
        exclude = ['employee', 'num_of_waqt_done', 'waqt_fajr']
        labels = {
            # "waqt_fajr": "Fazr",
            "waqt_zuhr": "Zuhr",
            "waqt_asr": "Asr",
            "waqt_maghrib": "Maghrib",
            "waqt_isha": "Esha",
        }
    
    def __init__(self, *args, **kwargs):
        super(EmployeePrayerInfoForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-check-input waqt_check'

