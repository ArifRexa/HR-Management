from django import forms
from employee.models.employee import Appointment

class AppointmentForm(forms.ModelForm):

    class Meta:
        model = Appointment
        fields = '__all__'
        