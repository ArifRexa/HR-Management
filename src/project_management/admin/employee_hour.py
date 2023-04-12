import datetime
from django.contrib import admin
from django.db.models import Q, Sum

from django.template.loader import get_template
from django.utils import timezone
from django.utils.html import format_html, linebreaks

from employee.admin.employee._forms import DailyUpdateFilterForm

from config.admin import RecentEdit
from config.admin.utils import simple_request_filter
from project_management.models import (
    EmployeeProjectHour,
    DailyProjectUpdate,
    DailyProjectUpdateAttachment
)

from project_management.models import DailyProjectUpdateHistory

class ProjectTypeFilter(admin.SimpleListFilter):
    title = 'hour type'
    parameter_name = 'project_hour__hour_type'

    def lookups(self, request, model_admin):
        return (
            ('project', 'Project'),
            ('bonus', 'Bonus'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'bonus':
            return queryset.filter(
                project_hour__hour_type='bonus',
            )
        elif self.value() == 'project':
            return queryset.filter(
                project_hour__hour_type='project',
            )

        return queryset


@admin.register(EmployeeProjectHour)
class EmployeeHourAdmin(RecentEdit, admin.ModelAdmin):
    list_display = ('get_date', 'employee', 'hours',
                    'get_hour_type', 'project_hour', )
    list_filter = (ProjectTypeFilter, 'employee', 'created_at',)
    search_fields = ('hours', 'employee__full_name',)
    date_hierarchy = 'project_hour__date'
    autocomplete_fields = ('employee', 'project_hour')
    change_list_template = 'admin/total.html'

    @admin.display(description="Date", ordering='project_hour__date')
    def get_date(self, obj):
        return obj.project_hour.date

    @admin.display(description="Hour Type", ordering='project_hour__hour_type')
    def get_hour_type(self, obj):
        return obj.project_hour.hour_type.title()

    def manager(self, obj):
        return obj.project_hour.manager

    # query for get total hour by query string
    def get_total_hour(self, request):
        qs = self.get_queryset(request).filter(
            **simple_request_filter(request))
        if not request.user.is_superuser and not request.user.has_perm("project_management.see_all_employee_hour"):
            if request.user.employee.manager:
                qs.filter(Q(project_hour__manager=request.user.employee.id) | Q(
                    employee=request.user.employee))
            else:
                qs.filter(employee=request.user.employee)
        return qs.aggregate(tot=Sum('hours'))['tot']

    # override change list view
    # return total hour count
    def changelist_view(self, request, extra_context=None):
        my_context = {
            'total': self.get_total_hour(request),
        }
        return super(EmployeeHourAdmin, self).changelist_view(request, extra_context=my_context)

    def get_queryset(self, request):
        """ Return query_set

        overrides django admin query set
        allow super admin and permitted user only to see all project hour
        manager's and employees will only see theirs
        @type request: object
        """
        query_set = super(EmployeeHourAdmin, self).get_queryset(request)
        if not request.user.is_superuser and not request.user.has_perm("project_management.see_all_employee_hour"):
            if request.user.employee.manager:
                return query_set.filter(
                    Q(project_hour__manager=request.user.employee.id) |
                    Q(employee=request.user.employee)
                )
            else:
                return query_set.filter(employee=request.user.employee)
        return query_set

    def get_list_filter(self, request):
        if not request.user.is_superuser and not request.user.has_perm("project_management.see_all_employee_hour"):
            return []
        return super(EmployeeHourAdmin, self).get_list_filter(request)

class DailyProjectUpdateDocumentAdmin(admin.TabularInline):
    model = DailyProjectUpdateAttachment
    extra = 0


@admin.register(DailyProjectUpdate)
class DailyProjectUpdateAdmin(admin.ModelAdmin):
    inlines = [DailyProjectUpdateDocumentAdmin, ]
    list_display = ('get_date', 'employee', 'project',  'history', 'manager', 'status_col')
    list_filter = ('status', 'project', 'employee', 'manager', )
    search_fields = ('employee__full_name', 'project__title',
                     'manager__full_name', )
    date_hierarchy = 'created_at'
    autocomplete_fields = ('employee', 'project', )
    change_list_template = 'admin/total_employee_hour.html'
    readonly_fields = ['status', 'created_at']
    actions = ['update_status_approve', 'update_status_pending']
    fieldsets = (
        ('Standard info', {
            'fields': ('created_at', 'employee', 'manager', 'project', 'hours', 'update', 'status')
        }),
    )

    class Media:
        css = {
            'all': ('css/list.css',)
        }
        js = ('js/list.js',)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ['created_at',]

        if obj:
            if request.user.employee.manager:
                if obj.manager != obj.employee and obj.manager == request.user.employee:
                    return ['created_at', 'employee', 'manager', 'project', 'update']
                else:
                    return ['created_at',]
            if request.user.employee == obj.employee:
                if obj.status == 'approved':
                    return ['created_at', 'employee', 'manager', 'project', 'update', 'hours', 'status']
                else:
                    return self.readonly_fields
            else:
                return self.readonly_fields

        else:
            if request.user.employee.manager:
                return ['created_at']
            else:
                return self.readonly_fields
    def history(self, obj):
        historyData = ""
        if obj.history is not None:
            for history in obj.history.order_by('-created_at'):
                historyData += f"{history.hours}"
                if history != obj.history.order_by('-created_at').last():
                     historyData += f" > "
            return format_html(historyData)

        return 'No changes'

    @admin.display(description="Date", ordering='created_at')
    def get_date(self, obj):
        return obj.created_at

    # @admin.display(description="Update")
    # def get_update(self, obj):
    #     html_template = get_template(
    #         'admin/project_management/list/col_dailyupdate.html')
    #     html_content = html_template.render({
    #         'update': obj.update,
    #     })
    #     return format_html(html_content)

    @admin.display(description="Hours", ordering='hours')
    def get_hours(self, obj):
        custom_style = ''
        if obj.hours <= 4:
            custom_style = ' style="color:red; font-weight: bold;"'
        html_content = f'<span{custom_style}>{obj.hours}</span>'
        return format_html(html_content)

    def changelist_view(self, request, extra_context=None):
        filter_form = DailyUpdateFilterForm(initial={
            'created_at__date__gte': request.GET.get('created_at__date__gte', timezone.now().date()-datetime.timedelta(days=7)),
            'created_at__date__lte': request.GET.get('created_at__date__lte', timezone.now().date())
        })
        my_context = {
            'total': self.get_total_hour(request),
            'filter_form': filter_form,
        }
        return super(DailyProjectUpdateAdmin, self).changelist_view(request, extra_context=my_context)

    def get_total_hour(self, request):
        qs = self.get_queryset(request).filter(
            **simple_request_filter(request))
        return qs.aggregate(tot=Sum('hours'))['tot']

    def get_queryset(self, request):
        query_set = super(DailyProjectUpdateAdmin, self).get_queryset(request)

        if not request.user.is_superuser and not request.user.has_perm("project_management.see_all_employee_update"):
            if request.user.employee.manager:
                query_set = query_set.filter(
                    Q(manager=request.user.employee) |
                    Q(employee=request.user.employee),
                )
            else:
                query_set = query_set.filter(employee=request.user.employee)

        return query_set

    def get_list_filter(self, request):
        filters = list(super(DailyProjectUpdateAdmin,
                       self).get_list_filter(request))
        if not request.user.is_superuser and not request.user.has_perm("project_management.see_all_employee_update"):
            if 'employee' in filters:
                filters.remove('employee')
        return filters

    def has_change_permission(self, request, obj=None):
        permitted = super().has_change_permission(request, obj=obj)
        if not request.user.is_superuser \
            and obj \
                and obj.employee != request.user.employee \
        and obj.manager != request.user.employee:
            permitted = False
        return permitted

    @admin.action(description='Status')
    def status_col(self, obj):
        color = 'red'
        if obj.status == 'approved':
            color = 'green'
        return format_html(
            f'<b style="color: {color}">{obj.get_status_display()}</b>'
        )

    @admin.action(description='Approve selected status daily project updates')
    def update_status_approve(modeladmin, request, queryset):
        if request.user.is_superuser:
            for obj in queryset:
                obj.status = 'approved'
                obj.save()
        elif request.user.employee.manager:
            queryset = queryset.filter(manager_id=request.user.employee.id)
            for obj in queryset:
                obj.status = 'approved'
                obj.save()

    @admin.action(description='Pending selected status daily project updates')
    def update_status_pending(modeladmin, request, queryset):
        if request.user.is_superuser:
            for obj in queryset:
                obj.status = 'pending'
                obj.save()
        elif request.user.employee.manager:
            queryset = queryset.filter(manager_id=request.user.employee.id)
            for obj in queryset:
                obj.status = 'pending'
                obj.save()
        # return

    def has_delete_permission(self, request, obj=None):
        permitted = super().has_delete_permission(request, obj=obj)
        if not request.user.is_superuser and obj and obj.employee != request.user.employee:
            permitted = False
        return permitted
    
    def save_model(self, request, obj, form, change) -> None:
        super().save_model(request, obj, form, change)
        
        if change == False:
            return DailyProjectUpdateHistory.objects.create(hours=request.POST.get('hours'), daily_update=obj)
            
        requested_hours = float(request.POST.get('hours'))
        if requested_hours != obj.hours or obj.created_by is not request.user:
            return DailyProjectUpdateHistory.objects.create(hours=request.POST.get('hours'), daily_update=obj)
        