import datetime

from django.contrib import admin
from django.http import JsonResponse
from django.template.loader import get_template
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.html import format_html
from django.views.decorators.csrf import csrf_exempt

from employee.models import EmployeeOnline, EmployeeAttendance, EmployeeActivity


@admin.register(EmployeeOnline)
class EmployeeOnlineAdmin(admin.ModelAdmin):
    list_display = ('employee', 'get_status', 'active')
    list_editable = ('active',)
    list_filter = ('active',)

    def get_queryset(self, request):
        query_set = super(EmployeeOnlineAdmin, self).get_queryset(request)
        if not request.user.is_superuser and not request.user.has_perm('employee.can_see_all_break'):
            return query_set.filter(employee=request.user.employee.id)
        return query_set

    @admin.display(description='Status')
    def get_status(self, obj):
        html_template = get_template('admin/employee_online/list/col_status.html')
        html_content = html_template.render({
            'employee_online': obj
        })
        return format_html(html_content)

    def get_urls(self):
        urls = super(EmployeeOnlineAdmin, self).get_urls()

        employee_online_urls = [
            path('employee-online-graph/', self.admin_site.admin_view(self.graph),
                 name='employee.online.graph'),
            path('employee-online-graph/<str:date>/', self.admin_site.admin_view(self.graph)),
            path('save-employee-online-status/', self.save_status)
        ]

        return employee_online_urls + urls

    @csrf_exempt
    def save_status(self, request):
        if request.method == 'POST':
            data = request.POST
            print(data.get('status'))
        return JsonResponse({'status': 200})

    def graph(self, request, *args, **kwargs):
        target_date = timezone.now().date()
        if 'date' in kwargs and parse_date(kwargs['date']) is not None:
            target_date = parse_date(kwargs['date'])

        employee_attendance = EmployeeAttendance.objects.filter(date=target_date).all()
        graph_data = []

        for attendance in employee_attendance:
            element = []
            breaks_timestamp = []
            for employee_break in attendance.employeeactivity_set.all():
                breaks_timestamp.append(int(employee_break.start_time.timestamp() * 1000))
                if employee_break.end_time:
                    breaks_timestamp.append(int(employee_break.end_time.timestamp() * 1000))
                else:
                    breaks_timestamp.append((int(timezone.now().timestamp() * 1000)))

            element.append(attendance.employee.full_name)
            element.append(breaks_timestamp)

            graph_data.append(element)

        context = dict(
            self.admin_site.each_context(request),
            graph_data=graph_data
        )
        return TemplateResponse(request, 'admin/employee_online/graph.html', context=context)


@admin.register(EmployeeAttendance)
class EmployeeAttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'employee', 'entry_time', 'exit_time')
    date_hierarchy = 'date'


@admin.register(EmployeeActivity)
class EmployeeBreakAdmin(admin.ModelAdmin):
    list_display = ('employee_attendance', 'start_time', 'end_time')
    date_hierarchy = 'employee_attendance__date'
