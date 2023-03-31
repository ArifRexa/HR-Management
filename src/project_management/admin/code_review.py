from django.contrib import admin, messages
from project_management.models import CodeReview, CodeReviewEmployeeFeedback
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


class CodeReviewEmployeeFeedbackInline(admin.StackedInline):
    model = CodeReviewEmployeeFeedback
    extra = 1

    # Returns true only when object owner or superuser
    def has_change_permission(self, request, obj=None):
        if obj and (request.user.is_superuser or obj.employee==request.user.employee):
            return True
        return False
    
    # Returns true only when object owner or superuser
    def has_add_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)
    

@admin.register(CodeReview)
class CodeReviewAdmin(admin.ModelAdmin):

    list_display = ['employee', 'manager', 'project', 'avg_rating', 'comment',]
    change_form_template = 'admin/code_review_form_full.html'

    inlines = (
        CodeReviewEmployeeFeedbackInline,
    )

    fieldsets = (
        ('Basic', {
            'fields': ('employee', 'manager', 'project', 'review_at')
        }),
        ('Ratings', {
            'fields': ('naming_convention', 'code_reusability', 'oop_principal', 'design_pattern', 'standard_git_commit'),
        }),
        ('Extras', {
            'fields': ('comment', ),
        }),
    )

    readonly_fields = ['avg_rating', 'for_first_quarter']
    list_filter = ['employee']
    search_fields = ['employee__full_name', "project__title", "avg_rating"]
    autocomplete_fields = (
        'project',
        'employee'
    )

    class Media:
        css = {
            'all': ('css/list.css',)
        }
        js = ('js/list.js',)

    def custom_changelist_view(self, request, extra_context=None):
        last_two_month = get_last_two_month()

        employees_list = list(Employee.objects.filter(active=True, project_eligibility=True).exclude(id__in=management_ids))

        # employees_list = sorted(employees_list, key=lambda item: (item.is_online))


        user_data = None
        for (index, emp) in enumerate(employees_list):
            if emp.user == request.user:
                user_data = employees_list.pop(index)
                break
        if user_data:
            employees_list.insert(0, user_data)

        full_data_set = dict()
        combined_monthly_total_datas = [[], []]
        last_date = None

        for index, employee in enumerate(employees_list):
            # code_review_set = employee.codereview_set.filter(created_at__gte=last_two_month[-1])
            temp = dict()
            last_date = None

            for month_num, month in enumerate(last_two_month):
                code_review_set = employee.codereview_set.filter(created_at__month=month.month, created_at__year=month.year).order_by('-created_at')
                first_quarter = code_review_set.filter(for_first_quarter=True)
                first_quarter_total = round(first_quarter.filter(for_first_quarter=True).aggregate(sum=Coalesce(Sum('avg_rating'), 0.0)).get("sum"), 1)
                last_quarter = code_review_set.filter(for_first_quarter=False)
                last_quarter_total = round(last_quarter.filter(for_first_quarter=False).aggregate(sum=Coalesce(Sum('avg_rating'), 0.0)).get("sum"), 1)

                monthly_total = round(code_review_set.aggregate(avg=Coalesce(Avg('avg_rating'), 0.0)).get("avg"), 1)
                # monthly_total = first_quarter_total+last_quarter_total

                if not last_date:
                    last_date = next(iter(item.created_at.date() for item in code_review_set or []), None)
                    # print(f"{employee.id} {employee.full_name} LAST DATE>>>")
                    # print(last_date)

                crs = {
                    "first_quarter": first_quarter,
                    "first_quarter_total": first_quarter_total if first_quarter_total else "-",
                    "last_quarter": last_quarter,
                    "last_quarter_total": last_quarter_total if last_quarter_total else "-",
                    "last_date": last_date if last_date else last_two_month[-1] - timedelta(days=1),
                }
                temp[month] = {
                    "monthly_total": monthly_total,
                    "crs": crs
                }
                combined_monthly_total_datas[month_num].append(monthly_total)

            full_data_set[employee] = temp

        last_two_month_dict = dict()
        for index, month in enumerate(last_two_month):
            last_two_month_dict[month] = sum(combined_monthly_total_datas[index])

        online_status_form = False
        if not str(request.user.employee.id) in management_ids:
            online_status_form = True

        order = request.GET.get('monthly_total', None)

        if order:
            if order in ['0', '1']:
                full_data_set = sorted(full_data_set.items(), key=lambda x: x[-1].get(last_two_month[int(order)], dict()).get('monthly_total', 0), reverse=True)
                order = True
            elif order in ['-0', '-1']:
                full_data_set = sorted(full_data_set.items(), key=lambda x: x[-1].get(last_two_month[int(order)], dict()).get('monthly_total', 0))
                order = False
            full_data_set = dict(full_data_set)
        else:
            full_data_set = dict(sorted(full_data_set.items(),
                                        key=lambda x: x[-1].get(last_two_month[-1]).get('crs', dict()).get('last_date'),
                                        reverse=True))
            full_data_set = sorted(full_data_set.items(),
                                   key=lambda x: x[-1].get(last_two_month[0]).get('crs', dict()).get('last_date'),
                                   reverse=True)
            full_data_set = dict(full_data_set)

        context = dict(
            self.admin_site.each_context(request),
            full_data_set=full_data_set,
            online_status_form=online_status_form,
            last_two_months=last_two_month_dict,
            order=order,
        )

        return TemplateResponse(request, 'admin/code_review.html', context)

    # def add_view(self, request, form_url='', extra_context=None):
    #     # employee_list = Employee.objects.filter(active=True, project_eligibility=True)
    #     return self.changeform_view(request, None, form_url, extra_context)

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
    
    def get_readonly_fields(self, request, obj=None):
        ro_fields = super().get_readonly_fields(request, obj)

        if not request.user.is_superuser and not request.user.has_perm('project_management.can_give_code_review'):
            ro_fields = (
                'employee', 'project', 
                'naming_convention', 'code_reusability', 'oop_principal', 'design_pattern', 'standard_git_commit', 'review_at',
                'comment',
            )

        return ro_fields
    

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if not request.user.is_superuser and not request.user.has_perm('project_management.can_give_code_review'):
            qs = qs.filter(employee=request.user.employee)

        return qs

