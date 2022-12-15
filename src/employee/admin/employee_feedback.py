import datetime

from django.contrib import admin, messages

from django.urls import path

from django.template.response import TemplateResponse

from django.shortcuts import redirect

from employee.models import EmployeeFeedback
from employee.forms.employee_feedback import EmployeeFeedbackForm


@admin.register(EmployeeFeedback)
class EmployeeFeedbackAdmin(admin.ModelAdmin):
    list_display = ('employee', 'feedback', 'rating')
    #list_editable = ('employee',)
    list_filter = ('employee', 'rating')
    search_fields = ('employee__full_name',)
    autocomplete_fields = ('employee',)

    def get_urls(self):
        urls = super(EmployeeFeedbackAdmin, self).get_urls()

        employee_online_urls = [
            path('employee-feedback/', self.employee_feedback, name='employee_feedback'),
        ]

        return employee_online_urls + urls

    def employee_feedback(self, request, *args, **kwargs):
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
                return redirect('/admin/')
            else:
                messages.error(request, 'Something went wrong')
                return redirect('/admin/')
        elif request.method == 'GET':
            form = EmployeeFeedbackForm(instance=employee_feedback_obj)

            context = dict(
                self.admin_site.each_context(request),
                employee_feedback_form=form,
            )
            
            return TemplateResponse(request, 'admin/form/employee_feedback_form.html', context)
