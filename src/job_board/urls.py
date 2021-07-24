from django.shortcuts import redirect
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from job_board.apis import job, authentication, assessment
from job_board.views import AssessmentPreview

urlpatterns = [
    path('api/', include([
        path('register-candidate/', authentication.Registration.as_view()),
        path('login/', authentication.Login.as_view()),
        path('candidate/', authentication.User.as_view()),
        path('send-otp/', authentication.SendOTP.as_view()),
        path('reset-password/', authentication.ResetPasswordView.as_view()),
        path('jobs/', job.JobList.as_view()),
        path('job/<str:slug>/', job.JobRetrieve.as_view()),
        path('apply/', job.CandidateJobView.as_view()),
        path('assessment/save-answer/', assessment.SaveAnswerView.as_view()),
        path('assessment/<str:unique_id>/', assessment.AssessmentRetrieve.as_view()),
    ])),
    path('preview-assessment/<int:pk>/', AssessmentPreview.as_view(), name='preview_assessment')
]

urlpatterns = format_suffix_patterns(urlpatterns)
