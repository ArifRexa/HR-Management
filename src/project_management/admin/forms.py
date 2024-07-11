from django import forms
from  project_management.models import ProjectTechnology,Project
class ProjectTechnologyInlineForm(forms.ModelForm):
    title = forms.CharField(label="Title", widget=forms.TextInput)

    class Meta:
        model = ProjectTechnology
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate choices with distinct titles
        distinct_titles = ProjectTechnology.objects.values_list('title', flat=True).distinct()
        choices = [(title, title) for title in distinct_titles]
        self.fields['title'].widget = forms.Select(choices=[('', '---')] + choices)
        self.fields['title'].widget.attrs.update({'class': 'select2'})  # Optional: Add CSS class for better UI


    
class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        # exclude = ['hourly_rate']