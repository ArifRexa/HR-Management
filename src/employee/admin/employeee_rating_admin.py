from collections.abc import Sequence
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.contrib import admin
from django import forms
from datetime import datetime, timedelta
from django.utils.html import format_html
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib import messages


from django.http.request import HttpRequest
from employee.models.employee_rating_models import EmployeeRating


class EmployeeRatingForm(forms.ModelForm):
    model = EmployeeRating
    # fields = "__all__"
    exclude = ('score',)

    def clean(self):
        clean_data = super().clean()
        request = self.request

        assigned_projects_titles = list(request.user.employee.employee_project_list.values_list('title', flat=True))
        rated_employee = clean_data.get('employee')
        rated_employee_projects = list(rated_employee.employee_project_list.values_list('title', flat=True))
        
        common_projects = list(set(assigned_projects_titles).intersection(set(rated_employee_projects)))
        print(common_projects)
        if not common_projects:
             raise forms.ValidationError(
                {"employee": "You cannot rate a employee who is not assosiated with your projects"}
            )

        if request.user.employee.id == self.cleaned_data.get("employee").id:
            raise forms.ValidationError(
                {"employee": "You cannot rate yourself. Plesae rate someone other."}
            )


        if clean_data.get("employee"):
            current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            current_month_end = current_month_start.replace(month=current_month_start.month + 1)
            is_provided = EmployeeRating.objects.filter(
                created_at__gte=current_month_start,
                created_at__lt=current_month_end,
                employee=clean_data.get("employee"),
                # project=clean_data.get("project"),
                created_by=request.user,
            ).exists()

            if is_provided:
                raise forms.ValidationError(
                    {"employee": "You have already given the rating for this employee in the current month. Please try again next month."}
                )

        return clean_data

@admin.register(EmployeeRating)
class EmployeeRatingAdmin(admin.ModelAdmin):
    list_display = [
        "employee",
        "rating_by",
        "project",
        "see_comment",
        "show_score",
        "created_at",
    ]
    fieldsets = (
    (
        None,
        {
            "fields": (
                'employee',
                'project',
                'performance_quality',
                'efficiency',
                'collaboration',
                'communication_effectiveness',
                'leadership_potential',
                'problem_solving_ability',
                'innovation_and_creativity',
                'adaptability_and_flexibility',
                'professional_growth_and_development',
                'overall_contribution_to_team_success',
                'comment',
            )
        },
    ),
)
    date_hierarchy = "created_at"
    list_filter = ["employee", "project"]
    autocomplete_fields = ["employee", "project"]
    form = EmployeeRatingForm

    class Media:
        css = {"all": ("css/list.css",)}
        js = ("js/list.js",)

    def get_employee(self):
        return 

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.has_perm("employee.can_view_all_ratings"):
            return qs
        return qs.filter(created_by__id=request.user.id)

    # def save_model(self, request, obj, form, change):
    #     # Check if there's already a rating submitted by the same user for the same employee in the current month
    #     current_month = timezone.now().month
    #     current_year = timezone.now().year
    #     existing_ratings = EmployeeRating.objects.filter(
    #         created_by=obj.created_by,
    #         employee=obj.employee,
    #         created_at__month=current_month,
    #         created_at__year=current_year
    #     )

    #     if existing_ratings.exists():
    #         # Show a message to the user instead of raising an error
    #         message = ("You have already submitted a rating for this employee this month. The new rating was not saved.")
    #         self.message_user(request, message, level=messages.WARNING)
    #         return

    #     # Call the save_model method of the parent class to save the object
    #     return super().save_model(request, obj, form, change)
    @admin.display(description="comments")
    def see_comment(self, obj):

        html_template = get_template("admin/employee/list/employe_rating_comments.html")
        html_content = html_template.render(
            {
             "comment": obj.comment
             }
        )
        return format_html(html_content)

    @admin.display(description="Show Score", ordering="score")
    def show_score(self, obj):
        string = f'<strong style="color:green">{obj.score}</strong>'
        if obj.score <= 5:
            string = f'<strong style="color:red">{obj.score}</strong>'
        return format_html(string)

    def has_delete_permission(self, request, obj=None):
        delete_or_update_before = datetime.now() + timedelta(days=7)
        if obj is None:
            return False

        if obj.created_at > delete_or_update_before:
            return False
        return True

    @admin.display(description="Rating By")
    def rating_by(self, obj):
        return f"{obj.created_by.employee.full_name}"

    def get_form(self, request, obj, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj == None:
            field = form.base_fields["employee"]
            field.widget.can_add_related = False
            field.widget.can_change_related = False
        form.request = request
        return form
    # @admin.display(description="comments")
    # def comment(self, obj):
    #     print('is it here ? ')
    #     html_template = "src/employee/templates/admin/employee/list/employe_rating_comments.html"
    #     context = {'obj': obj}  # Pass the obj as a context variable
    #     return render_to_string(html_template, context)
