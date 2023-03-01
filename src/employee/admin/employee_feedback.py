import datetime
from functools import update_wrapper
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from config.settings import employee_ids
from django.contrib import admin, messages
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.contrib.auth.models import AnonymousUser
from django.template.response import TemplateResponse

from django.db import models
from django.db.models import Max, Subquery, OuterRef, Case, When, Value, Prefetch

from django.shortcuts import redirect
from employee.models.employee_feedback import CommentAgainstEmployeeFeedback
from employee.models import EmployeeFeedback, Employee
from employee.forms.employee_feedback import EmployeeFeedbackForm


def get_last_months(start_date):
    for _ in range(3):
        yield start_date.month
        start_date += relativedelta(months=-1)

class CommentAgainstEmployeeFeedbackInline(admin.StackedInline):
    model = CommentAgainstEmployeeFeedback
    extra = 1

    def has_change_permission(self, request, obj= None):
        if obj and (request.user.is_superuser or request.user.has_perm('employee.can_see_employee_feedback_admin')):
            return True
        return False
   
    def has_add_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

@admin.register(EmployeeFeedback)
class EmployeeFeedbackAdmin(admin.ModelAdmin):
    # list_display = ('employee','feedback')
    # #list_editable = ('employee',)
    # list_filter = ('employee', 'rating')
    # search_fields = ('employee__full_name',)
    # autocomplete_fields = ('employee',)

    inlines = (
        CommentAgainstEmployeeFeedbackInline,
    )

    def custom_changelist_view(self, request, *args, **kwargs) -> TemplateResponse:
        if str(request.user.employee.id) not in employee_ids and not request.user.has_perm('employee.can_see_employee_feedback_admin'):
            return redirect('/admin/')

        months = [
            'January',
            'February',
            'March',
            'April',
            'May',
            'June',
            'July',
            'August',
            'September',
            'October',
            'November',
            'December'
        ]

        six_months = [i for i in get_last_months(datetime.datetime.today())]

        six_months_names = [months[i-1] for i in six_months]

        order_keys = {
            '1': 'last_feedback_rating',
            '-1': '-last_feedback_rating',
        }

        order_by = ['-current_feedback_exists', '-last_feedback_date']

        o=request.GET.get('o', None)
        if o and o in order_keys.keys():
            order_by.insert(1, order_keys.get(o))

        e_fback_qs = EmployeeFeedback.objects.filter(
                        employee=OuterRef('pk'), 
                        updated_at__month=timezone.now().date().month,
                    )

        employees = Employee.objects.filter(active=True).annotate(
            last_feedback_date=Max('employeefeedback__updated_at'),
            last_feedback_rating=Subquery(e_fback_qs.values('avg_rating')[:1]),
            current_feedback_exists=Case(
                When(last_feedback_rating=None, then=Value(False)),
                default=Value(True),
                output_field=models.BooleanField(),
            ),
        ).order_by(*order_by)

        monthly_feedbacks = list()
        for e in employees:
            temp = []
            for month in six_months:
                for fback in e.last_x_months_feedback:
                    if month == fback.created_at.month:
                        temp.append(fback)
                        break
                else:
                    temp.append(None)
            monthly_feedbacks.append(temp)
        context = dict(
                self.admin_site.each_context(request),
                month_names=six_months_names,
                monthly_feedbacks=zip(employees, monthly_feedbacks),
                o=o, # order key
            )
        return TemplateResponse(request, 'admin/employee_feedback/employee_feedback_admin.html', context)

    list_display = ('employee', 'environmental_rating', 'facilities_rating', 'learning_growing_rating', 'avg_rating')
    list_filter = ('employee', 'avg_rating')
    search_fields = ('employee__full_name',)
    autocomplete_fields = ('employee',)

    # def get_urls(self):
    #     urls = super(EmployeeFeedbackAdmin, self).get_urls()

    #     employee_online_urls = [
    #         path('my-feedback/', self.employee_feedback_view, name='employee_feedback'),
    #         path('my-feedback-form/', self.employee_feedback_form_view, name='employee_feedback_form'),
    #     ]
    #     return employee_online_urls + urls

    def get_urls(self):
        urls = super(EmployeeFeedbackAdmin, self).get_urls()

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name
        custome_urls = [
            path("admin/", wrap(self.changelist_view), name="%s_%s_changelist" % info),

            path("", self.custom_changelist_view, name='employee_feedback'),

            path('my-feedback/', self.employee_feedback_view, name='employee_feedback'),
            path('my-feedback-form/', self.employee_feedback_form_view, name='employee_feedback_form'),
        ]
        return custome_urls + urls


    def employee_feedback_view(self, request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser):
            return redirect('/admin/login/')

        if request.method == 'GET':
            current_feedback_exists = EmployeeFeedback.objects.filter(
                employee=request.user.employee, 
                created_at__gte=datetime.datetime.today().replace(day=1)
            ).exists()
            employee_feedback_objs = EmployeeFeedback.objects.filter(
                employee=request.user.employee
            ).order_by('-created_at')
            
            form = EmployeeFeedbackForm()
            
            context = dict(
                self.admin_site.each_context(request),
                employee_feedback_form=form,
                employee_feedback_objs=employee_feedback_objs,
                current_feedback_exists=current_feedback_exists,
            )
            return TemplateResponse(request, 'admin/employee_feedback/employee_feedback.html', context)


    def employee_feedback_form_view(self, request, *args, **kwargs):
        employee_feedback_obj = EmployeeFeedback.objects.filter(
                employee=request.user.employee, 
                created_at__gte=datetime.datetime.today().replace(day=1)
            ).first()
        if request.method == 'POST':
            form = EmployeeFeedbackForm(request.POST, instance=employee_feedback_obj)
            if form.is_valid():
                form = form.save(commit=False)
                form.employee = request.user.employee
                form.save()
                messages.success(request, 'Your feedback has been submitted successfully')
                return redirect('admin:employee_feedback')
            else:
                messages.error(request, 'Something went wrong')
                return redirect('admin:employee_feedback')
        elif request.method == 'GET':
            form = EmployeeFeedbackForm(instance=employee_feedback_obj)

            context = dict(
                self.admin_site.each_context(request),
                employee_feedback_form=form,
            )
            
            return TemplateResponse(request, 'admin/employee_feedback/employee_feedback_form_full.html', context)

    def get_readonly_fields(self, request, obj):
        if request.user.is_superuser and request.user.has_perm('employee.can_see_employee_feedback_admin'):
           return ['employee','feedback','avg_rating','environmental_rating','facilities_rating','learning_growing_rating','happiness_index_rating','boss_rating']
        return []
    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)

    #     # if request.user.is_superuser and request.user.has_perm('can_see_employee_feedback_admin'):
    #     #     qs = qs.filter(employee = request.user.employee)

    #     return qs 