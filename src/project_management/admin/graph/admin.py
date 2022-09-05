import datetime
import itertools

from django.contrib import admin
from django.core.serializers import serialize
from django.db.models import Func, F, Value, CharField, Sum, Count, Field
from django.db.models.functions import TruncMonth, Cast, TruncDate
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.dateparse import parse_datetime

from project_management.models import Project, ProjectHour


class ExtraUrl(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        project_management_urls = [
            path('graph/', self.admin_site.admin_view(self.graph, cacheable=False),
                 name='project_management.hour.graph'),
            path('project-gaph/', self.admin_site.admin_view(self.project_graph, cacheable=False),
                 name='project_management.project.graph')
        ]
        return project_management_urls + urls

    def graph(self, request, *args, **kwargs):
        context = dict(
            self.admin_site.each_context(request),
            title='Monthly Hour Graph',
            series=self.get_data(request)
        )
        return TemplateResponse(request, "admin/graph/monthly.html", context=context)

    def project_graph(self, request, *args, **kwargs):
        active_projects = []
        for item in self.get_project_query('created_at').filter(active=True).values('month', 'total_project'):
            active_projects.append([
                int(parse_datetime(item['month']).timestamp()),
                item['total_project']
            ])
        inactive_projects = []
        for item in self.get_project_query('updated_at').filter(active=False).values('month', 'total_project'):
            inactive_projects.append([
                int(parse_datetime(item['month']).timestamp()),
                item['total_project']
            ])

        context = dict(
            self.admin_site.each_context(request),
            title='Project Graph',
            active_projects=active_projects,
            inactive_projects=inactive_projects
        )
        return TemplateResponse(request, "admin/graph/project.html", context=context)

    def get_project_query(self, cast_field: str):
        base_query = Project.objects.annotate(month=Cast(TruncMonth(cast_field), CharField())) \
            .values('month') \
            .annotate(total_project=Count('id'))
        return base_query

    def get_data(self, request):
        series = list()
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
                'name': project.title,
                'data': list(array_date)
            })

        sum_hours = ProjectHour.objects.filter(date__gte=date_to_check).extra(
            select={'date_str': 'UNIX_TIMESTAMP(date)*1000'}
        ).order_by('date').values_list('date_str').annotate(Sum('hours'))
        sum_array = []
        for sum_hour in sum_hours:
            sum_array.append(list(sum_hour))
        series.append({
            'type': 'spline',
            'name': 'Total Project Hours',
            'data': sum_array
        })
        return series
