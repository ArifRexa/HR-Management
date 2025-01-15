from datetime import datetime

from django.urls import path
from project_management.views import get_this_week_hour, slack_callback, generate_client_weekly_report

from django.urls import path, register_converter


class DateConverter:
    regex = '\d{4}-\d{1,2}-\d{1,2}'
    format = '%Y-%m-%d'

    def to_python(self, value):
        return datetime.strptime(value, self.format).date()

    def to_url(self, value):
        return value.strftime(self.format)


register_converter(DateConverter, 'date')


urlpatterns = [
    path('get-this-week-hour/<int:project_id>/<date:hour_date>/', get_this_week_hour),
    path('slack/', slack_callback),
    path('project-weekly-report/<int:project_id>/<date:hour_date>/', generate_client_weekly_report),
]
