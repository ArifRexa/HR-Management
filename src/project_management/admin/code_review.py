from django.contrib import admin, messages
from project_management.models import CodeReview
from django.utils import timezone
from datetime import datetime, timedelta
from employee.models import Employee
from django.template.response import TemplateResponse
from functools import partial, update_wrapper, wraps
from django.urls import path
from django.db.models import Count, Sum, Avg
from django.db.models.functions import Coalesce
from config.settings import employee_ids as management_ids




def get_last_two_month():
    this_month_start = timezone.now().date().replace(day=1)
    previous_month_end = this_month_start - timedelta(days=1)
    previous_month_start = previous_month_end.replace(day=1)

    return this_month_start, previous_month_start


@admin.register(CodeReview)
class CodeReviewAdmin(admin.ModelAdmin):
    list_display = ['employee', 'project', 'avg_rating', 'comment']
    fields = [
        ('employee', 'project'),
        ('naming_convention', 'code_reusability'),
        ('oop_principal', 'design_pattern', 'standard_git_commit'),
        ('comment')
    ]
    readonly_fields = ['avg_rating', 'for_first_quarter']
    list_filter = ['employee']
    search_fields = ['employee__full_name', "project__title", "avg_rating"]

    class Media:
        css = {
            'all': ('css/list.css',)
        }
        js = ('js/list.js',)

    def custom_changelist_view(self, request, extra_context=None):
        last_two_month = get_last_two_month()

        employees_list = Employee.objects.filter(active=True).exclude(id__in=management_ids)

        employees_list = sorted(employees_list, key=lambda item: (item.is_online))

        user_data = None
        for (index, emp) in enumerate(employees_list):
            if emp.user == request.user:
                user_data = employees_list.pop(index)
                break
        if user_data:
            employees_list.insert(0, user_data)

        full_data_set = dict()

        for index, employee in enumerate(employees_list):
            # code_review_set = employee.codereview_set.filter(created_at__gte=last_two_month[-1])
            temp = dict()
            for month in last_two_month:
                code_review_set = employee.codereview_set.filter(created_at__month=month.month, created_at__year=month.year).order_by('-created_at')
                first_quarter = code_review_set.filter(for_first_quarter=True)
                first_quarter_total = round(first_quarter.filter(for_first_quarter=True).aggregate(sum=Coalesce(Sum('avg_rating'), 0.0)).get("sum"), 1)
                last_quarter = code_review_set.filter(for_first_quarter=False)
                last_quarter_total = round(last_quarter.filter(for_first_quarter=False).aggregate(sum=Coalesce(Sum('avg_rating'), 0.0)).get("sum"), 1)

                monthly_total = round(code_review_set.aggregate(avg=Coalesce(Avg('avg_rating'), 0.0)).get("avg"), 1)
                # monthly_total = first_quarter_total+last_quarter_total

                crs = {
                    "first_quarter": first_quarter,
                    "first_quarter_total": first_quarter_total if first_quarter_total else "-",
                    "last_quarter": last_quarter,
                    "last_quarter_total": last_quarter_total if last_quarter_total else "-",
                    # "last_date": last_quarter[0].created_at if last_quarter_total else "-",
                }
                temp[month] = {
                    "monthly_total": monthly_total,
                    "crs": crs
                }

            full_data_set[employee] = temp

        online_status_form = False
        if not str(request.user.employee.id) in management_ids:
            online_status_form = True

        # full_data_set = sorted(full_data_set.items(), key=lambda x: datetime.now().date() if x[-1].get(datetime.now().date(), dict()).get('crs', dict()).get('first_quarter', CodeReview()).created_at is None else datetime.now().date())
        # full_data_set = sorted(full_data_set.items(), key=lambda x: x[-1].get(last_two_month[0], dict()).get('crs', dict()).get('last_date', datetime.now().date()))

        context = dict(
            self.admin_site.each_context(request),
            full_data_set=full_data_set,
            online_status_form=online_status_form,
            last_two_months=last_two_month,
        )

        return TemplateResponse(request, 'admin/code_review.html', context)

    def get_urls(self):
        urls = super(CodeReviewAdmin, self).get_urls()

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name
        custome_urls = [
            path("admin/", wrap(self.changelist_view), name="%s_%s_changelist" % info),

            path("", self.custom_changelist_view, name='code_review'),
        ]
        return custome_urls + urls

