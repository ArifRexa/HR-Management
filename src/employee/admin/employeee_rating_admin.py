from datetime import datetime, timedelta
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.template.loader import get_template
from django.utils import timezone
from django.db.models import Case, When, Q, Value, Sum
from django.db.models.functions import Coalesce
from employee.models.employee_rating_models import EmployeeRating
from employee.models import Employee


class EmployeeRatingForm(forms.ModelForm):
    model = EmployeeRating
    # fields = "__all__"
    exclude = ("score",)

    # project = forms.ModelChoiceField(
    #     queryset=Project.objects.none(),
    # )
    # employee = forms.ModelChoiceField(
    #     queryset=Employee.objects.none(),
    # )

    # def __init__(self, *args, **kwargs):
    #     super(EmployeeRatingForm, self).__init__(*args, **kwargs)
    #     projects = Project.objects.filter(
    #         employeeproject__employee__user=self.request.user
    #     )
    #     self.fields['project'].queryset = projects

    #     associated_employees = Employee.objects.filter(
    #         employeeproject__project__in=projects
    #     )
    #     self.fields['employee'].queryset = associated_employees

    def clean(self):
        clean_data = super().clean()
        request = self.request
        rated_employee = clean_data.get("employee")
        if rated_employee is None:
            raise forms.ValidationError({"employee": "Please Select an Employee"})

        if request.user.employee.id == self.cleaned_data.get("employee").id:
            raise forms.ValidationError(
                {"employee": "You cannot rate yourself. Plesae rate someone other."}
            )

        if clean_data.get("employee"):
            current_month_start = datetime.now().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            current_month_end = current_month_start.replace(
                month=current_month_start.month + 1
            )
            # is_provided = EmployeeRating.objects.filter(
            #     created_at__gte=current_month_start,
            #     created_at__lt=current_month_end,
            #     employee=clean_data.get("employee"),
            #     created_by=request.user,
            # ).exists()

            today = datetime.now()

            employee = Employee.objects.get(user__id=request.user.id)
            joining_datetime = datetime.combine(
                employee.joining_date, datetime.min.time()
            )
            days_since_joining = (timezone.now() - joining_datetime).days

            # if days_since_joining > 30:
            #     # Worst Case
            #     if today.month == 1:
            #         previous_month_rating_complete = EmployeeRating.objects.filter(
            #             Q(created_by_id=request.user.id)
            #             & Q(month=12)
            #             & Q(year=today.year - 1)
            #         ).exists()
            #     else:
            #         previous_month_rating_complete = EmployeeRating.objects.filter(
            #             Q(created_by_id=request.user.id)
            #             & Q(month=today.month - 1)
            #             & Q(year=today.year)
            #         ).exists()

            #     if not previous_month_rating_complete:
            #         if (
            #             clean_data.get("month") == today.month
            #             and clean_data.get("year") == today.year
            #         ):
            #             raise forms.ValidationError(
            #                 {
            #                     "month": "You have to provide rating for the previous month."
            #                 }
            #             )

            is_provided = EmployeeRating.objects.filter(
                month=clean_data.get("month"),
                year=clean_data.get("year"),
                employee=clean_data.get("employee"),
                created_by=request.user,
            ).exists()
            print(is_provided and self.instance.id is None)
            if is_provided and self.instance.id is None:
                raise forms.ValidationError(
                    {
                        "employee": "You have already given the rating for this employee in the current month. Please try again next month."
                    }
                )

        return clean_data


class EmployeeRatingFilterByScoreTitle(admin.SimpleListFilter):
    title = "Score Title"
    parameter_name = "title"

    def lookups(self, request, model_admin):
        return (
            ("Poor", "Poor"),
            ("Needs Improvement", "Needs Improvement"),
            ("Fair", "Fair"),
            ("Good", "Good"),
            ("Excellent", "Excellent"),
        )

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.annotate(
                score_title=Case(
                    When(Q(score__lte=9, score__gte=1), then=Value("Poor")),
                    When(
                        Q(score__lte=15, score__gte=10), then=Value("Needs Improvement")
                    ),
                    When(Q(score__lte=19, score__gte=16), then=Value("Fair")),
                    When(Q(score__lte=22, score__gte=20), then=Value("Good")),
                    When(Q(score__lte=25, score__gte=23), then=Value("Excellent")),
                )
            ).filter(score_title=self.value())
        else:
            return queryset


@admin.register(EmployeeRating)
class EmployeeRatingAdmin(admin.ModelAdmin):
    list_display = [
        "employee",
        "rating_by",
        "see_comment",
        "show_score",
        "get_last_six_months_score",
        "month",
        "year",
        "created_at",
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "month",
                    "year",
                    "employee",
                    "score",
                    # "project",
                    # "feedback_responsiveness",
                    # "continuous_learning",
                    # "collaboration",
                    # "communication_effectiveness",
                    # "leadership_potential",
                    # "problem_solving_ability",
                    # "innovation_and_creativity",
                    # "adaptability_and_flexibility",
                    # "professional_growth_and_development",
                    # "overall_contribution_to_team_success",
                    "comment",
                )
            },
        ),
    )
    date_hierarchy = "created_at"
    list_filter = ["employee", EmployeeRatingFilterByScoreTitle]
    autocomplete_fields = [
        "employee",
    ]
    form = EmployeeRatingForm

    class Media:
        css = {"all": ("css/list.css",)}
        js = ("js/list.js", "js/employee_rating.js")

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
        html_content = html_template.render({"comment": obj.comment})
        return format_html(html_content)

    def get_score_title_last_six_months(self, score):
        if score in range(1, 55): # range exclude 1 from 55
            return "Poor"
        elif score in range(55, 91):
            return "Needs Improvement"
        elif score in range(91, 115):
            return "Fair"
        elif score in range(115, 133):
            return "Good"
        elif score in range(133, 151):
            return "Excellent"
        else:
            return "N/A"
        

    @admin.display(description="Last Six Months Score")
    def get_last_six_months_score(self, obj):
        employee_rating = EmployeeRating.objects.filter(
            employee=obj.employee, created_at__lte=obj.created_at
        ).order_by("-created_at")[:6]
        total_score = employee_rating.aggregate(
            total_score=Coalesce(Sum("score"), 0)
        ).get("total_score", 0)
        title = self.get_score_title_last_six_months(total_score)
        string = f'<strong style="color:green">{total_score}/{title}({len(employee_rating)})</strong>'
        if obj.score <= 54:
            string = f'<strong style="color:red">{total_score}/{title}({len(employee_rating)})</strong>'
        return format_html(string)

    def get_score_title(self, score):
        if score in range(1, 10): # range exclude 1 from 10
            return "Poor"
        elif score in range(10, 16):
            return "Needs Improvement"
        elif score in range(16, 20):
            return "Fair"
        elif score in range(20, 23):
            return "Good"
        elif score in range(23, 26):
            return "Excellent"
        else:
            return "N/A"

    @admin.display(description="Show Score", ordering="score")
    def show_score(self, obj):
        title = self.get_score_title(obj.score)
        string = f'<strong style="color:green">{obj.score}/{title}</strong>'
        if obj.score <= 9:
            string = f'<strong style="color:red">{obj.score}/{title}</strong>'
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
