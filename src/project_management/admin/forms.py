from django import forms
from  project_management.models import ProjectTechnology

class ProjectTechnologyInlineForm(forms.ModelForm):
    title = forms.ModelChoiceField(queryset=ProjectTechnology.objects.values_list('title', flat=True).distinct())

    class Meta:
        model = ProjectTechnology
        fields = '__all__'
