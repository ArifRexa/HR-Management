from django.shortcuts import redirect
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from job_board.views.apis import job, authentication, assessment
from job_board.views.webpages.views import WebsiteView, MailView

webview_urls = [
    path('email-view/', MailView.as_view()),
    path('job-board/', WebsiteView.as_view())
]

api_urls = [
    path('register-candidate/', authentication.Registration.as_view(), name='jb_registration'),
    path('login/', authentication.Login.as_view(), name='jb_login'),
    path('candidate/', authentication.User.as_view(), name='jb_candidate'),
    path('send-otp/', authentication.SendOTP.as_view(), name='jb_send_otp'),
    path('reset-password/', authentication.ResetPasswordView.as_view(), name='jb_reset_password'),
    path('jobs/', job.JobList.as_view(), name='jb_jobs'),
    path('job/<str:slug>/', job.JobRetrieve.as_view(), name='jb_job'),
    path('apply/', job.CandidateJobView.as_view(), name='jb_job_apply'),
    path('assessment/', assessment.CandidateAssessmentList.as_view(), name='jb_assessments'),
    path('assessment/save-answer/', assessment.SaveAnswerView.as_view(), name='jb_save_answer'),
    path('assessment/save-evaluation-url/', assessment.SaveEvaluationUrl.as_view(), name='jb_save_evl_url'),
    path('assessment/<str:unique_id>/', assessment.CandidateAssessmentView.as_view(), name='jb_assessment'),
    # GET, POST
    path('assessment/<str:unique_id>/question/', assessment.CandidateAssessmentQuestion.as_view(),
         name='fetch_question'),  # GET
]

urlpatterns = [
    path('api/', include(api_urls)),
    path('', include(webview_urls))
]

urlpatterns = format_suffix_patterns(urlpatterns)
