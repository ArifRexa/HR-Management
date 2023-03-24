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
from django.db.models import Prefetch, Count, Q

# Needed for optional Features
# from django.db.models import Count, Case, When, Value, BooleanField
from django.shortcuts import redirect

from employee.models import EmployeeOnline, EmployeeAttendance, EmployeeActivity, Employee, PrayerInfo
from employee.models.employee_activity import EmployeeProject
from employee.forms.prayer_info import EmployeePrayerInfoForm

from project_management.models import EmployeeProjectHour
from config.settings import employee_ids as management_ids


def sToTime(duration):
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

        # from account.tasks import create_all_pfaccount
        # create_all_pfaccount()
        
        now = timezone.now()
        DEFAULT_EXIT_HOUR = 12 + 9 # 24 Hour time == 9 pm
        DEFAULT_EXIT_TIME = now.replace(hour=DEFAULT_EXIT_HOUR, minute=0, second=0)

        last_x_dates = [(now - datetime.timedelta(i)).date() for i in range(30)]
        last_x_date = (now - datetime.timedelta(30)).date()

        last_month = (now.replace(day=1) - datetime.timedelta(days=1)).date()

        emps = Employee.objects.filter(
            active=True,
            show_in_attendance_list=True,
        ).order_by(
            'full_name'
        ).prefetch_related(
            Prefetch(
                "employeeattendance_set",
                queryset=EmployeeAttendance.objects.filter(
                    date__gte=last_x_date
                ).prefetch_related("employeeactivity_set")
            ),
            Prefetch(
                "prayerinfo_set",
                queryset=PrayerInfo.objects.filter(
                    created_at__date__gte=last_x_date,
                ),
            ),
            Prefetch(
                "employeeprojecthour_set",
                queryset=EmployeeProjectHour.objects.filter(
                    project_hour__date__gte=last_x_date,
                    project_hour__hour_type='bonus',
                ).select_related("project_hour"),
            ),
        ).annotate(
            last_month_attendance=Count(
                "employeeattendance",
                filter=Q(
                    employeeattendance__date__year=last_month.year,
                    employeeattendance__date__month=last_month.month,
                ),
            )
        )

        # dates = [*range(1, calendar.monthrange(now.year, now.month)[1]+1)]

        emps = sorted(emps, key=lambda item: (item.is_online))
        user_data = None
        for (index, emp) in enumerate(emps):
            if emp.user == request.user:
                user_data = emps.pop(index)
                break
        if user_data:
            emps.insert(0, user_data)

        date_datas = {}

        for emp in emps:
            temp = {}
            attendances = emp.employeeattendance_set.all()
            prayerinfos = emp.prayerinfo_set.all()
            empprojhours = emp.employeeprojecthour_set.all()
            for date in last_x_dates:
                temp[date] = dict()

                for eph in reversed(empprojhours):
                    if eph.project_hour.date == date:
                        pass 
                        # temp[date].update({
                        #     'bonus_hour': int(eph.hours),
                        # })
                        break

                for pinfo in prayerinfos:
                    if pinfo.created_at.date() == date and pinfo.num_of_waqt_done > 0:
                        waqts = []
                        if pinfo.waqt_fajr: waqts.append('F')
                        if pinfo.waqt_zuhr: waqts.append('Z')
                        if pinfo.waqt_asr: waqts.append('A')
                        if pinfo.waqt_maghrib: waqts.append('M')
                        if pinfo.waqt_isha: waqts.append('E')
                        prayer_info_text = '(' + ' '.join(waqts) +')'
                        temp[date].update({
                            'prayer_count': pinfo.num_of_waqt_done,
                            'prayer_info': prayer_info_text,
                        })

                for attendance in attendances:
                    if attendance.date == date:
                        activities = attendance.employeeactivity_set.all()
                        if activities.exists():
                            activities = list(activities)
                            al = len(activities)
                            start_time = activities[0].start_time
                            end_time = activities[-1].end_time
                            is_updated_by_bot = activities[-1].is_updated_by_bot
                            break_time = 0
                            inside_time = 0

                            for i in range(al-1):
                                et = activities[i].end_time
                                if et and et.date() == activities[i+1].start_time.date():
                                    break_time += (activities[i+1].start_time.timestamp() - et.timestamp())
                            for i in range(al):
                                st, et = activities[i].start_time, activities[i].end_time
                                if not et:
                                    # if not now.hour < DEFAULT_EXIT_HOUR:
                                    #     if st.hour < DEFAULT_EXIT_HOUR:
                                    #         et = DEFAULT_EXIT_TIME
                                    #     else:
                                    #         et = st
                                    # else:
                                    et = timezone.now()
                                inside_time += (et.timestamp() - st.timestamp())

                            break_time_s = sToTime(break_time)
                            inside_time_s = sToTime(inside_time)

                            temp[date].update({
                                'entry_time': start_time.time() if start_time else '-',
                                'exit_time': end_time.time() if end_time else '-',
                                'is_updated_by_bot': is_updated_by_bot,
                                'break_time': break_time_s,
                                'break_time_hour': math.floor((break_time / (60 * 60)) % 24),
                                'inside_time': inside_time_s,
                                'inside_time_hour': math.floor((inside_time / (60 * 60)) % 24),
                            })
                        break
            date_datas.update({emp: temp})

        prayerobj = PrayerInfo.objects.filter(employee=request.user.employee, created_at__date=now.date()).last()
        form = EmployeePrayerInfoForm(instance=prayerobj)

        online_status_form = False
        if not str(request.user.employee.id) in management_ids:
            online_status_form = True

        o=request.GET.get('o', None)

        if o:
            if o == 'entry':
                date_datas_sorted = sorted(date_datas.items(), key=lambda x: x[-1].get(datetime.datetime.now().date(), datetime.datetime.now().date()).get('entry_time', DEFAULT_EXIT_TIME.time()))
                o = '-entry'
            elif o == '-entry':
                date_datas_sorted = sorted(date_datas.items(), key=lambda x: x[-1].get(datetime.datetime.now().date(),
                                                                                       datetime.datetime.now().date()).get(
                    'entry_time', DEFAULT_EXIT_TIME.time()), reverse=True)
                o = 'entry'

            date_datas = dict(date_datas_sorted)

        context = dict(
                self.admin_site.each_context(request),
                dates=last_x_dates,
                last_month=last_month,
                date_datas=date_datas,
                o=o, # order key
                form=form,
                online_status_form=online_status_form
            )
        return TemplateResponse(request, 'admin/employee/employee_attendance.html', context)

    def waqt_select(self, request, *args, **kwargs) -> redirect:
        if not request.user.is_authenticated:
            return redirect('/')
        if request.method == 'POST':
            prayerobj = PrayerInfo.objects.filter(employee=request.user.employee, created_at__date=timezone.now().date()).last()
            form = EmployeePrayerInfoForm(request.POST, instance=prayerobj)
            if form.is_valid():
                prayer_info = form.save(commit=False)
                prayer_info.employee = request.user.employee
                prayer_info.save()
                messages.success(request, 'Submitted Successfully')

        return redirect("admin:employee_attendance")

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
            path("waqtselect/", self.waqt_select, name='waqt_select')
        ]
        return employee_online_urls + urls

    # def has_module_permission(self, request):
    #     return False


@admin.register(EmployeeActivity)
class EmployeeBreakAdmin(admin.ModelAdmin):
    list_display = ('employee_attendance', 'get_start_time', 'get_end_time')
    date_hierarchy = 'employee_attendance__date'
    autocomplete_fields = ('employee_attendance',)
    list_filter = ('employee_attendance__employee',)
    search_fields = ('employee_attendance__employee__full_name',)
    # readonly_fields = ('start_by', 'end_by',)


    # @admin.display(description='Created By', ordering="created_by")
    # def get_created_by(self, obj):
    #     return obj.created_by.employee.full_name

    @admin.display(description='Start Time', ordering="start_time")
    def get_start_time(self, obj):
        start_time = ''

        if obj.start_time:
            start_time += obj.start_time.strftime("%b %d, %Y, %I:%M %p")

            if obj.created_by and obj.created_by != obj.employee_attendance.employee.user:
                start_time += '<span style="color: red; font-weight: bold;"> (' + obj.created_by.employee.full_name + ')</span>'

        return format_html(start_time)


    @admin.display(description='End Time', ordering="end_time")
    def get_end_time(self, obj):
        end_time = ''

        if obj.end_time:
            end_time += obj.end_time.strftime("%b %d, %Y, %I:%M %p")

            if obj.updated_by and obj.updated_by != obj.employee_attendance.employee.user:
                end_time += '<span style="color: red; font-weight: bold;"> (' + obj.updated_by.employee.full_name + ')</span>'

        return format_html(end_time)

    # To hide from main menu
    # def has_module_permission(self, request):
    #     return False


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


@admin.register(PrayerInfo)
class EmployeePrayerInfoAdmin(admin.ModelAdmin):
    list_display = ('get_date', 'employee', 'num_of_waqt_done' )
    autocomplete_fields = ('employee', )
    list_filter = ('employee', )
    search_fields = ('employee__full_name', )

    @admin.display(description="Date", ordering="created_at")
    def get_date(self, obj, *args, **kwargs):
        return obj.created_at.strftime("%b %d, %Y")

    def has_module_permission(self, request):
        return False

