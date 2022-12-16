import datetime

from django.contrib import admin, messages

from django.urls import path

from django.template.response import TemplateResponse

from django.shortcuts import redirect

from employee.models import EmployeeFeedback
from employee.forms.employee_feedback import EmployeeFeedbackForm


@admin.register(EmployeeFeedback)
class EmployeeFeedbackAdmin(admin.ModelAdmin):
    list_display = ('employee', 'feedback', 'avg_rating')
    #list_editable = ('employee',)
    list_filter = ('employee', 'avg_rating')
    search_fields = ('employee__full_name',)
    autocomplete_fields = ('employee',)

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

