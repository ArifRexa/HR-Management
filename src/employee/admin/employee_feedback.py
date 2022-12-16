import datetime
from dateutil.relativedelta import relativedelta

from django.contrib import admin, messages

from django.urls import path

from django.template.response import TemplateResponse

from django.shortcuts import redirect

from employee.models import EmployeeFeedback, Employee
from employee.forms.employee_feedback import EmployeeFeedbackForm


def get_last_months(start_date):
    start_date += relativedelta(months = -1)
    for _ in range(6):
        yield start_date.month
        start_date += relativedelta(months = -1)


@admin.register(EmployeeFeedback)
class EmployeeFeedbackAdmin(admin.ModelAdmin):
    # list_display = ('employee',)
    # #list_editable = ('employee',)
    # list_filter = ('employee', 'rating')
    # search_fields = ('employee__full_name',)
    # autocomplete_fields = ('employee',)

    def changelist_view(self, request, *args, **kwargs) -> TemplateResponse:
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

        employees = Employee.objects.all()

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
            )
        return TemplateResponse(request, 'admin/employee_feedback/employee_feedback_admin.html', context)


    def get_urls(self):
        urls = super(EmployeeFeedbackAdmin, self).get_urls()

        employee_online_urls = [
            path('employee-feedback/', self.employee_feedback_view, name='employee_feedback'),
            path('employee-feedback-form/', self.employee_feedback_form_view, name='employee_feedback_form'),
        ]

        return employee_online_urls + urls
    

    def employee_feedback_view(self, request, *args, **kwargs):
        if request.method == 'GET':
            current_feedback_exists = EmployeeFeedback.objects.filter(
                employee=request.user.employee, 
                created_at__gte=datetime.datetime.today().replace(day=1)
            ).exists()
            employee_feedbac_objs = EmployeeFeedback.objects.filter(
                employee=request.user.employee
            ).order_by('-created_at')
            
            form = EmployeeFeedbackForm()
            
            context = dict(
                self.admin_site.each_context(request),
                employee_feedback_form=form,
                employee_feedbac_objs=employee_feedbac_objs,
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

