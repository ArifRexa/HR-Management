from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from job_board.apis import job, authentication, assessment

urlpatterns = [
    path('api/', include([
        path('register-candidate/', authentication.Registration.as_view()),
        path('login/', authentication.Login.as_view()),
        path('job/', job.JobList.as_view()),
        path('job/<str:slug>/', job.JobRetrieve.as_view()),
        path('apply/', job.CandidateJobView.as_view()),
        path('assessment/<str:unique_id>/', assessment.AssessmentRetrieve.as_view()),
        path('assessment/<str:slug>/<int:pk>', assessment.AssessmentQuestionRetrieve.as_view())
    ]))
]

urlpatterns = format_suffix_patterns(urlpatterns)
