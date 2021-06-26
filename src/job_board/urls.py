from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from job_board.apis import job

urlpatterns = [
    path('', job.ActiveJobList.as_view()),
    path('<str:slug>/', job.JobDetail.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
