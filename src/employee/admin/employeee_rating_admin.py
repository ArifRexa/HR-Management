from datetime import datetime, timedelta
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.template.loader import get_template
from django.utils import timezone
from django.db.models import Case, When, Q, Value, Sum, Avg
from django.db.models.functions import Coalesce
# from employee.models.employee_rating_models import EmployeeRating
from employee.models import Employee


# class EmployeeRatingForm(forms.ModelForm):
#     model = EmployeeRating
#     # fields = "__all__"
#     exclude = ("score",)

#     # project = forms.ModelChoiceField(
#     #     queryset=Project.objects.none(),
#     # )
#     # employee = forms.ModelChoiceField(
#     #     queryset=Employee.objects.none(),
#     # )

#     # def __init__(self, *args, **kwargs):
#     #     super(EmployeeRatingForm, self).__init__(*args, **kwargs)
#     #     projects = Project.objects.filter(
#     #         employeeproject__employee__user=self.request.user
#     #     )
#     #     self.fields['project'].queryset = projects

#     #     associated_employees = Employee.objects.filter(
#     #         employeeproject__project__in=projects
#     #     )
#     #     self.fields['employee'].queryset = associated_employees

#     def clean(self):
#         clean_data = super().clean()
#         request = self.request
#         rated_employee = clean_data.get("employee")
#         if rated_employee is None:
#             raise forms.ValidationError({"employee": "Please Select an Employee"})

#         if request.user.employee.id == self.cleaned_data.get("employee").id:
#             raise forms.ValidationError(
#                 {"employee": "You cannot rate yourself. Plesae rate someone other."}
#             )

#         if clean_data.get("employee"):
#             current_month_start = datetime.now().replace(
#                 day=1, hour=0, minute=0, second=0, microsecond=0
#             )
#             current_month_end = current_month_start.replace(
#                 month=current_month_start.month + 1
#             )
#             # is_provided = EmployeeRating.objects.filter(
#             #     created_at__gte=current_month_start,
#             #     created_at__lt=current_month_end,
#             #     employee=clean_data.get("employee"),
#             #     created_by=request.user,
#             # ).exists()

#             today = datetime.now()

#             employee = Employee.objects.get(user__id=request.user.id)
#             joining_datetime = datetime.combine(
#                 employee.joining_date, datetime.min.time()
#             )
#             days_since_joining = (timezone.now() - joining_datetime).days

#             # if days_since_joining > 30:
#             #     # Worst Case
#             #     if today.month == 1:
#             #         previous_month_rating_complete = EmployeeRating.objects.filter(
#             #             Q(created_by_id=request.user.id)
#             #             & Q(month=12)
#             #             & Q(year=today.year - 1)
#             #         ).exists()
#             #     else:
#             #         previous_month_rating_complete = EmployeeRating.objects.filter(
#             #             Q(created_by_id=request.user.id)
#             #             & Q(month=today.month - 1)
#             #             & Q(year=today.year)
#             #         ).exists()

#             #     if not previous_month_rating_complete:
#             #         if (
#             #             clean_data.get("month") == today.month
#             #             and clean_data.get("year") == today.year
#             #         ):
#             #             raise forms.ValidationError(
#             #                 {
#             #                     "month": "You have to provide rating for the previous month."
#             #                 }
#             #             )

#             is_provided = EmployeeRating.objects.filter(
#                 month=clean_data.get("month"),
#                 year=clean_data.get("year"),
#                 employee=clean_data.get("employee"),
#                 created_by=request.user,
#             ).exists()
#             print(is_provided and self.instance.id is None)
#             if is_provided and self.instance.id is None:
#                 raise forms.ValidationError(
#                     {
#                         "employee": "You have already given the rating for this employee in the current month. Please try again next month."
#                     }
#                 )

#         return clean_data


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


# @admin.register(EmployeeRating)
# class EmployeeRatingAdmin(admin.ModelAdmin):
    
#     list_display = [
#         "employee",
#         # "rating_by",
#         # "see_comment",
#         "current_month_average_display",
#         "last_month_average_display",
#         "third_last_month_average_display",  # Display for third last month
#         "fourth_last_month_average_display",  # Display for fourth last month
#         "fifth_last_month_average_display",  # Display for fifth last month
#         "sixth_last_month_average_display",
#     ]
#     fieldsets = (
#         (
#             None,
#             {
#                 "fields": (
#                     "month",
#                     "year",
#                     "employee",
#                     "rating_overall_satisfaction",
#                     "communication_effectiveness",
#                     "rating_quality_of_work",
#                     "rating_time_management",
#                     "rating_understanding_of_requirements",
#                     "overall_contribution_to_team_success",
#                     "professional_growth_and_development",
#                     "problem_solving_ability",
#                     "collaboration",
#                     "leadership_potential",
#                     "adaptability_and_flexibility",
#                     "comment",
#                 )
#             },
#         ),
#     )
#     date_hierarchy = "created_at"
#     list_filter = ["employee", EmployeeRatingFilterByScoreTitle]
#     autocomplete_fields = [
#         "employee",
#     ]
#     # form = EmployeeRatingForm

#     change_form_template = "admin/employee_rating/employee_add_form.html"

#     class Media:
#         css = {"all": ("css/list.css",)}
#         js = ("js/list.js", "js/employee_rating.js")

#     def get_employee(self):
#         return

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if request.user.has_perm("employee.can_view_all_ratings"):
#             return qs
#         return qs.filter(created_by__id=request.user.id)

#     def add_view(self, request, form_url='', extra_context=None):
#         # For add_view, we don't have an object, so pass `None` to get_form
#         form = self.get_form(request, None)()
#         extra_context = extra_context or {}
#         extra_context['adminform'] = admin.helpers.AdminForm(
#             form, list(self.get_fieldsets(request)), self.get_prepopulated_fields(request)
#         )
#         return super().add_view(request, form_url, extra_context=extra_context)

#     def change_view(self, request, object_id, form_url='', extra_context=None):
#         # Get the object by its ID for change_view
#         obj = self.get_object(request, object_id)
#         form = self.get_form(request, obj)(instance=obj)
#         extra_context = extra_context or {}
#         extra_context['adminform'] = admin.helpers.AdminForm(
#             form, list(self.get_fieldsets(request, obj)), self.get_prepopulated_fields(request, obj)
#         )
#         return super().change_view(request, object_id, form_url, extra_context=extra_context)

#     def save_model(self, request, obj, form, change):
#         # Get the current month and year
#         current_month = obj.month
#         current_year = obj.year
#         employee = obj.employee

#         # Check if a rating already exists for the same employee in the current month and year
#         existing_rating = EmployeeRating.objects.filter(
#             employee=employee,
#             month=current_month,
#             year=current_year
#         ).exclude(id=obj.id)  # Exclude the current object if it's an edit

#         if existing_rating.exists():
#             print("$"*45)
#             print(existing_rating)
#             # Show a message to the user that a rating already exists
#             self.message_user(request, "You have already submitted a rating for this employee in the current month.")
#             return  # Prevent saving the new rating

#         # Call the parent class's save_model method to save the object
#         super().save_model(request, obj, form, change)

#     @admin.display(description="Current Month Average")
#     def current_month_average_display(self, obj):
#         average = self.get_month_average(obj.employee, 0)  # Current month
#         return f"{average:.2f}" if average is not None else "No Data"

#     @admin.display(description="Last Month Average")
#     def last_month_average_display(self, obj):
#         average = self.get_month_average(obj.employee, 1)  # Last month
#         return f"{average:.2f}" if average is not None else "No Data"

#     @admin.display(description="Third Last Month Average")
#     def third_last_month_average_display(self, obj):
#         average = self.get_month_average(obj.employee, 2)  # Third last month
#         return f"{average:.2f}" if average is not None else "No Data"

#     @admin.display(description="Fourth Last Month Average")
#     def fourth_last_month_average_display(self, obj):
#         average = self.get_month_average(obj.employee, 3)  # Fourth last month
#         return f"{average:.2f}" if average is not None else "No Data"

#     @admin.display(description="Fifth Last Month Average")
#     def fifth_last_month_average_display(self, obj):
#         average = self.get_month_average(obj.employee, 4)  # Fifth last month
#         return f"{average:.2f}" if average is not None else "No Data"

#     @admin.display(description="Sixth Last Month Average")
#     def sixth_last_month_average_display(self, obj):
#         average = self.get_month_average(obj.employee, 5)  # Sixth last month
#         return f"{average:.2f}" if average is not None else "No Data"

#     def get_month_average(self, employee, months_ago):
#         now = timezone.now()
        
#         # Calculate the first day of the month for the month we are interested in
#         month_year = now - timedelta(days=months_ago * 30)
#         first_day = month_year.replace(day=1)

#         # Calculate the last day of the month
#         if month_year.month == 12:  # December case
#             last_day = first_day.replace(year=first_day.year + 1, month=1, day=1) - timedelta(days=1)
#         else:
#             last_day = first_day.replace(month=first_day.month + 1, day=1) - timedelta(days=1)

#         # Query for ratings in the specified month
#         ratings = EmployeeRating.objects.filter(
#             employee=employee,
#             created_at__gte=first_day,
#             created_at__lte=last_day
#         )

#         if not ratings.exists():
#             return None  # No ratings found for that month

#         # Calculate average for relevant fields
#         averages = ratings.aggregate(
#             overall_satisfaction=Avg('rating_overall_satisfaction'),
#             communication_effectiveness=Avg('communication_effectiveness'),
#             quality_of_work=Avg('rating_quality_of_work'),
#             time_management=Avg('rating_time_management'),
#             understanding_of_requirements=Avg('rating_understanding_of_requirements'),
#             contribution_to_team_success=Avg('overall_contribution_to_team_success'),
#             growth_and_development=Avg('professional_growth_and_development'),
#             problem_solving=Avg('problem_solving_ability'),
#             collaboration=Avg('collaboration'),
#             leadership=Avg('leadership_potential'),
#             adaptability=Avg('adaptability_and_flexibility'),
#         )

#         # Calculate overall average for the month, ignoring None values
#         total_average = sum(filter(None, averages.values())) / len(averages)
#         return round(total_average, 2)  # Round to 2 decimal places


#     @admin.display(description="comment")
#     def see_comment(self, obj):
#         html_template = get_template("admin/employee/list/employe_rating_comments.html")
#         html_content = html_template.render({"comment": obj.comment})
#         return format_html(html_content)

#     def get_score_title_last_six_months(self, score):
#         if score in range(1, 55): # range exclude 1 from 55
#             return "Poor"
#         elif score in range(55, 91):
#             return "Needs Improvement"
#         elif score in range(91, 115):
#             return "Fair"
#         elif score in range(115, 133):
#             return "Good"
#         elif score in range(133, 151):
#             return "Excellent"
#         else:
#             return "N/A"
 

#     @admin.display(description="Last Six Months Score")
#     def get_last_six_months_score(self, obj):
#         employee_rating = EmployeeRating.objects.filter(
#             employee=obj.employee, created_at__lte=obj.created_at
#         ).order_by("-created_at")[:6]
#         total_score = employee_rating.aggregate(
#             total_score=Coalesce(Sum("score"), 0)
#         ).get("total_score", 0)
#         title = self.get_score_title_last_six_months(total_score)
#         string = f'<strong style="color:green">{total_score}/{title}({len(employee_rating)})</strong>'
#         if obj.score <= 54:
#             string = f'<strong style="color:red">{total_score}/{title}({len(employee_rating)})</strong>'
#         return format_html(string)

#     def get_score_title(self, score):
#         if score in range(1, 10): # range exclude 1 from 10
#             return "Poor"
#         elif score in range(10, 16):
#             return "Needs Improvement"
#         elif score in range(16, 20):
#             return "Fair"
#         elif score in range(20, 23):
#             return "Good"
#         elif score in range(23, 26):
#             return "Excellent"
#         else:
#             return "N/A"

#     @admin.display(description="Show Score", ordering="score")
#     def show_score(self, obj):
#         title = self.get_score_title(obj.score)
#         string = f'<strong style="color:green">{obj.score}/{title}</strong>'
#         if obj.score <= 9:
#             string = f'<strong style="color:red">{obj.score}/{title}</strong>'
#         return format_html(string)

#     def has_delete_permission(self, request, obj=None):
#         delete_or_update_before = datetime.now() + timedelta(days=7)
#         if obj is None:
#             return False

#         if obj.created_at > delete_or_update_before:
#             return False
#         return True

#     # @admin.display(description="Rating By")
#     # def rating_by(self, obj):
#     #     return f"{obj.created_by.employee.full_name}"

#     # def get_form(self, request, obj, **kwargs):
#     #     form = super().get_form(request, obj, **kwargs)
#     #     if obj == None:
#     #         field = form.base_fields["employee"]
#     #         field.widget.can_add_related = False
#     #         field.widget.can_change_related = False
#     #     form.request = request
#     #     return form

#     # @admin.display(description="comments")
#     # def comment(self, obj):
#     #     print('is it here ? ')
#     #     html_template = "src/employee/templates/admin/employee/list/employe_rating_comments.html"
#     #     context = {'obj': obj}  # Pass the obj as a context variable
#     #     return render_to_string(html_template, context)
