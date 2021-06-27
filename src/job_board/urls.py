from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from job_board.apis import job, authentication

urlpatterns = [
    path('api/', include([
        path('job/', job.JobList.as_view()),
        path('job/<str:slug>/', job.JobRetrieve.as_view()),
        path('apply/', job.CandidateJobView.as_view()),
        path('register-candidate/', authentication.Registration.as_view()),
        path('login/', authentication.Login.as_view())
    ]))
]

urlpatterns = format_suffix_patterns(urlpatterns)
