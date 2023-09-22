from django import forms

from employee.models import EmployeeNeedHelp


class EmployeeNeedHelpForm(forms.ModelForm):
    class Meta:
        model = EmployeeNeedHelp
        fields = ["need_help_position"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["need_help_position"].widget.attrs.update({"hidden": "hidden"})
