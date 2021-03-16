from django import forms
from .models import JobApply

class JobApplyForm(forms.ModelForm):
    class Meta:
        model = JobApply
        fields = [
            'data',
            'file',
        ]