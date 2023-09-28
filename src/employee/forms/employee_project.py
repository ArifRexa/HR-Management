from django import forms

from employee.models.employee_activity import EmployeeProject


class EmployeeProjectForm(forms.ModelForm):
    class Meta:
        model = EmployeeProject
        fields = ["project"]

    def __init__(self, *args, **kwargs):
        super(EmployeeProjectForm, self).__init__(*args, **kwargs)
        self.fields["project"].widget.attrs.update({"hidden": "hidden"})
