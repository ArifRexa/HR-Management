from typing import Any
from django import forms
from project_management.models import ProjectTechnology, Project
from website.models_v2.services import ServicePage


class ProjectTechnologyInlineForm(forms.ModelForm):
    title = forms.CharField(label="Title", widget=forms.TextInput)

    class Meta:
        model = ProjectTechnology
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate choices with distinct titles
        distinct_titles = ProjectTechnology.objects.values_list(
            "title", flat=True
        ).distinct()
        choices = [(title, title) for title in distinct_titles]
        self.fields["title"].widget = forms.Select(choices=[("", "---")] + choices)
        self.fields["title"].widget.attrs.update(
            {"class": "select2"}
        )  # Optional: Add CSS class for better UI


class ProjectAdminForm(forms.ModelForm):
    services = forms.ModelChoiceField(
        queryset=ServicePage.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={
                "class": "select2",
            }
        ),
        empty_label='------'
    )

    class Meta:
        model = Project
        fields = "__all__"
        # exclude = ['hourly_rate']
        widgets = {
            "description": forms.Textarea(
                attrs={"cols": 100, "rows": 2, "style": "resize: none;"}
            )
        }

    def __init__(self, *args, **kwargs):
        super(ProjectAdminForm, self).__init__(*args, **kwargs)
        self.fields['services'].label_from_instance = self.custom_service_label

    def custom_service_label(self, obj):
        return obj.menu_title

    def clean(self):
        if self.cleaned_data.get("featured_video") and not self.cleaned_data.get(
            "thumbnail"
        ):
            raise forms.ValidationError(
                "Thumbnail Required when Featured Video is Provided"
            )
        return super().clean()
