import datetime
import json
from datetime import timedelta

from django.contrib import admin

from django.core.exceptions import ValidationError
from django import forms
# Register your models here.
from django.db.models import Sum, Q, F
from django.template.context_processors import request
from django.utils import timezone
from django.template.loader import get_template
from django.utils.html import format_html
from config.admin import ExportCsvMixin, RecentEdit
from config.admin.utils import simple_request_filter
from project_management.admin.project_hour.actions import ProjectHourAction
from project_management.admin.project_hour.options import ProjectHourOptions
from project_management.models import Client, Project, ProjectHour, EmployeeProjectHour


class EmployeeHourAdmin(admin.TabularInline):
    model = EmployeeProjectHour
    extra = 1
    autocomplete_fields = ('employee',)

    def get_readonly_fields(self, request, obj=None):
        three_day_earlier = timezone.now() - timedelta(days=2)
        if obj is not None:
            if obj.created_at <= three_day_earlier and not request.user.is_superuser:
                return ('hours', 'employee')
        return ()


class ProjectHourAdminForm(forms.ModelForm):

     def clean(self):
        data = super(ProjectHourAdminForm, self).clean()
        if data.get('hour_type') != "bonus":
            if self.request:
                if self.request.path_info[-5:-1] == "/add":
                    project = data.get('project')
                    if project and ProjectHour.objects.filter(
                        manager_id=self.request.user.employee.id, 
                        project_id=project.id, 
                        date=data.get('date')
                    ).exists():
                        raise ValidationError({
                            'date': "Project Hour for this date with this project and manager already exists",
                        })
            return data

@admin.register(ProjectHour)
class ProjectHourAdmin(ProjectHourAction, ProjectHourOptions, RecentEdit, admin.ModelAdmin):
    date_hierarchy = 'date'
    search_fields = ['hours', 'manager__full_name', 'project__title', 'date']
    inlines = (EmployeeHourAdmin,)
    change_list_template = 'admin/total.html'
    autocomplete_fields = ['project']
    list_per_page = 50
    ordering = ('-pk',)
    add_form_template = 'admin/project_hour/project_hour.html'
    fieldsets = (
        ('Standard info', {
            'fields': ('hour_type', 'project', 'date', 'hours')
        }),
        (
            'Administration Process', {
                'fields': ('operation_feedback','client_exp_feedback', 'approved_by_cto')
            }
        )
    )
    form = ProjectHourAdminForm

    def get_form(self, request, obj, change, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.request = request
        return form

    # query for get total hour by query string
    def get_total_hour(self, request):
        qs = self.get_queryset(request).filter(
            **simple_request_filter(request))
        if not request.user.is_superuser:
            qs.filter(manager__id__exact=request.user.employee.id)
        return qs.aggregate(tot=Sum('hours'))['tot']

    # override change list view
    # return total hour count
    def changelist_view(self, request, extra_context=None):
        my_context = {
            'total': self.get_total_hour(request),
            'series': self.get_data(request)

        }
        return super(ProjectHourAdmin, self).changelist_view(request, extra_context=my_context)

    def get_queryset(self, request):
        """ Return query_set

        overrides django admin query set
        allow super admin only to see all project hour
        manager's will only see theirs
        @type request: object
        """
        query_set = super(ProjectHourAdmin, self).get_queryset(request)
        if not request.user.is_superuser and not request.user.has_perm('project_management.show_all_hours'):
            return query_set.filter(manager_id=request.user.employee.id)
        return query_set

    def save_model(self, request, obj, form, change):
        """
        override project hour save
        manager id will be authenticate user employee id if the user is not super user
        """
        if not obj.manager_id:
            obj.manager_id = request.user.employee.id

        super(ProjectHourAdmin, self).save_model(request, obj, form, change)

    def get_fieldsets(self, request, obj):
        fieldsets = super(ProjectHourAdmin, self).get_fieldsets(request, obj)
        if not request.user.has_perm('project_management.weekly_project_hours_approve'):
            return (fieldsets[0], )

        return fieldsets

    def get_data(self, request):
        series = list()
        selected_projects = self.get_changelist_instance(request).get_filters_params().get('project__id__exact')
        if selected_projects:
            projects = Project.objects.filter(id__in=selected_projects, active=True).all()
        else:
            projects = Project.objects.filter(active=True).all()
        date_to_check = datetime.date.today() - datetime.timedelta(days=60)
        for project in projects:
            data = project.projecthour_set.filter(date__gte=date_to_check).extra(
                select={'date_str': "UNIX_TIMESTAMP(date)*1000"}
            ).order_by('date').values_list('date_str', 'hours')
            # TODO : must be optimize otherwise it will effect the load time
            array_date = []
            for value in data:
                array_date.append(list(value))

            series.append({
                'type': 'spline',
                # 'visible': 'false',
                'name': project.title,
                'data': list(array_date)
            })
        if selected_projects:
            sum_hours = ProjectHour.objects.filter(project_id__in=selected_projects, date__gte=date_to_check).extra(
                select={'date_str': 'UNIX_TIMESTAMP(date)*1000'}
            ).order_by('date').values_list('date_str').annotate(Sum('hours'))
        else:
            sum_hours = ProjectHour.objects.filter(date__gte=date_to_check).extra(
                select={'date_str': 'UNIX_TIMESTAMP(date)*1000'}
            ).order_by('date').values_list('date_str').annotate(Sum('hours'))
        sum_array = []
        # for sum_hour in sum_hours:
        #     sum_array.append(list(sum_hour)) #  it will return the total hours of projects.
        series.append({
            'type': 'spline',
            'name': 'Total Project Hours',
            'data': sum_array
        })
        return series

    # def get_data(self, request):
    #     series = []
    #     selected_projects = self.get_changelist_instance(request).get_filters_params().get('project__id__exact')
    #
    #     if selected_projects:
    #         projects = Project.objects.filter(id__in=selected_projects, active=True).all()
    #     else:
    #         projects = Project.objects.filter(active=True).all()
    #
    #     date_to_check = datetime.date.today() - datetime.timedelta(days=60)
    #
    #     for project in projects:
    #         data = project.projecthour_set.filter(date__gte=date_to_check).extra(
    #             select={'date_str': "UNIX_TIMESTAMP(date)*1000"}
    #         ).order_by('date').values_list('date_str', 'hours')
    #
    #         array_date = []
    #         for value in data:
    #             array_date.append(list(value))
    #
    #         series.append({
    #             'type': 'spline',
    #             'name': project.title,
    #             'data': list(array_date)
    #         })
    #
    #     # Calculate total project hours for filtered projects only
    #     if selected_projects:
    #         sum_hours = ProjectHour.objects.filter(project_id__in=selected_projects, date__gte=date_to_check).extra(
    #             select={'date_str': 'UNIX_TIMESTAMP(date)*1000'}
    #         ).order_by('date').values_list('date_str').annotate(Sum('hours'))
    #
    #         sum_array = []
    #         for sum_hour in sum_hours:
    #             sum_array.append(list(sum_hour))
    #
    #         series.append({
    #             'type': 'spline',
    #             'name': 'Total Project Hours',
    #             'data': sum_array
    #         })
    #
    #     return series

