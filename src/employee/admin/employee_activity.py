import datetime, calendar, math
from functools import update_wrapper

from django.contrib import admin, messages
from django.http import JsonResponse
from django.template.loader import get_template
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.html import format_html
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Prefetch

# Needed for optional Features
# from django.db.models import Count, Case, When, Value, BooleanField
from django.shortcuts import redirect

from employee.models import EmployeeOnline, EmployeeAttendance, EmployeeActivity, Employee
from employee.models.employee_activity import EmployeeProject


def msToTime(duration):
    minutes = math.floor((duration / 60) % 60)
    hours = math.floor((duration / (60 * 60)) % 24)

    return f"{hours:01}h: {minutes:01}m"


@admin.register(EmployeeOnline)
class EmployeeOnlineAdmin(admin.ModelAdmin):
    list_display = ('employee', 'get_status', 'active')
    list_editable = ('active',)
    list_filter = ('active',)
    search_fields = ('employee__full_name',)
    autocomplete_fields = ('employee',)

    def get_queryset(self, request):
        EmployeeOnline.objects.filter()
        query_set = super(EmployeeOnlineAdmin, self).get_queryset(request)
        if not request.user.is_superuser and not request.user.has_perm('employee.can_see_all_break'):
            return query_set.filter(employee=request.user.employee.id)
        return query_set.filter(employee__active=True).exclude(employee_id__in=[7, 30, 76, 49])

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
            # path('employee-online-graph/<str:date>/', self.admin_site.admin_view(self.graph)),
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

        if 'date' in request.GET and parse_date(request.GET.get('date')):
            target_date = parse_date(request.GET.get('date'))

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
    
    def has_module_permission(self, request):
        return False


@admin.register(EmployeeAttendance)
class EmployeeAttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'employee', 'entry_time', 'exit_time')
    date_hierarchy = 'date'
    list_filter = ('employee',)
    search_fields = ('employee__full_name', 'date')
    autocomplete_fields = ('employee',)

    def custom_changelist_view(self, request, *args, **kwargs) -> TemplateResponse:
        if not request.user.is_authenticated:
            return redirect('/')
        
        now = timezone.now()

        last_x_dates = [(now - datetime.timedelta(i)).date() for i in range(30)]
        last_x_date = (now - datetime.timedelta(30)).date()
        
        emps = Employee.objects.filter(
            active=True
        ).order_by(
            'full_name'
        ).prefetch_related(
            Prefetch(
                "employeeattendance_set", 
                queryset=EmployeeAttendance.objects.filter(
                    date__gte=last_x_date
                ).prefetch_related("employeeactivity_set")
            ),
        )

        # dates = [*range(1, calendar.monthrange(now.year, now.month)[1]+1)]

        date_datas = {}
        
        for emp in emps:
            temp = {}
            attendances = emp.employeeattendance_set.all()
            for date in last_x_dates:
                temp[date] = None
                for attendance in attendances:
                    if attendance.date == date:
                        activities = attendance.employeeactivity_set.all()
                        if activities.exists():
                            activities = list(activities)
                            al = len(activities)
                            start_time = activities[0].start_time
                            end_time = activities[-1].end_time
                            break_time = 0

                            for i in range(al-1):
                                et = activities[i].end_time
                                if et:
                                    break_time += (activities[i+1].start_time.timestamp() - et.timestamp())
                            
                            break_time = msToTime(break_time)

                            temp[date] = {
                                'entry_time': start_time.time() if start_time else '-',
                                'exit_time': end_time.time() if end_time else '-',
                                'break_time': break_time,
                            }
                        break
            date_datas.update({emp: temp})
        
        o=request.GET.get('o', None)
        context = dict(
                self.admin_site.each_context(request),
                dates=last_x_dates,
                date_datas=date_datas,
                o=o, # order key
            )
        return TemplateResponse(request, 'admin/employee/employee_attendance.html', context)

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        urls = super(EmployeeAttendanceAdmin, self).get_urls()

        employee_online_urls = [
            path("admin/", wrap(self.changelist_view), name="%s_%s_changelist" % info),
            
            path("", self.custom_changelist_view, name='employee_attendance'),
        ]
        return employee_online_urls + urls
    
    def has_module_permission(self, request):
        return False


@admin.register(EmployeeActivity)
class EmployeeBreakAdmin(admin.ModelAdmin):
    list_display = ('employee_attendance', 'start_time', 'end_time')
    date_hierarchy = 'employee_attendance__date'
    autocomplete_fields = ('employee_attendance',)
    list_filter = ('employee_attendance__employee',)
    search_fields = ('employee_attendance__employee__full_name',)

    def has_module_permission(self, request):
        return False


@admin.register(EmployeeProject)
class EmployeeProjectAdmin(admin.ModelAdmin):
    list_display = ('employee', 'get_projects')
    autocomplete_fields = ('employee', 'project')
    list_filter = ('project',)
    search_fields = ('employee__full_name', 'project__title')

    # Can be used when hide employees without projects
    # If used, no project can be assigned by admin due to onetoone field

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     return qs.annotate(
    #         project_count=Count("project"),
    #         project_exists=Case(
    #             When(project_count=0, then=Value(False)),
    #             default=Value(True),
    #             output_field=BooleanField()
    #         )
    #     ).filter(project_exists=True)

    @admin.display(description='Projects')
    def get_projects(self, obj):
        projects = ' | '.join(obj.project.filter(active=True).values_list('title', flat=True))
        if projects == '':
            projects = '-'
        return projects

    def has_module_permission(self, request):
        return False
