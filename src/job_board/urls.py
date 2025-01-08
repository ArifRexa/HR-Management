from django.shortcuts import redirect
from django.urls import path, include, register_converter
from rest_framework.urlpatterns import format_suffix_patterns

from job_board.views.apis import (job, authentication, assessment, VivaConfigViewSet,
                                  JobVivaTimeSlotCreateAPIView, VivaConfigPerDayViewSet)
# from job_board.views.apis.authentication import ApplicationSummaryView, get_months, get_emails
from job_board.views.webpages.views import WebsiteView, MailView
from datetime import datetime


class DateConverter:
    regex = '\d{4}-\d{1,2}-\d{1,2}'
    format = '%Y-%m-%d'

    def to_python(self, value):
        return datetime.strptime(value, self.format).date()

    def to_url(self, value):
        return value.strftime(self.format)


register_converter(DateConverter, 'date')


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
    path('change-password/', authentication.ChangeCandidatePassword.as_view(), name='jb_change_password'),

    path('jobs/', job.JobList.as_view(), name='jb_jobs'),
    path('job/<str:slug>/', job.JobRetrieve.as_view(), name='jb_job'),
    path('apply/', job.CandidateJobView.as_view(), name='jb_job_apply'),
    path('candidate-job/<str:unique_id>/', assessment.CandidateJobRetrieve.as_view(), name='jb_candidate_job'),

    path('assessment/', assessment.CandidateAssessmentList.as_view(), name='jb_assessments'),
    path('assessment/save-answer/', assessment.SaveAnswerView.as_view(), name='jb_save_answer'),
    path('assessment/save-evaluation-url/', assessment.SaveEvaluationUrl.as_view(), name='jb_save_evl_url'),
    path('assessment/<str:unique_id>/', assessment.CandidateAssessmentView.as_view(), name='jb_assessment'),
    # GET, POST
    path('assessment/<str:unique_id>/question/', assessment.CandidateAssessmentQuestion.as_view(),
         name='fetch_question'),  # GET
    path('total-viva-slot-via-job-id/<int:job_id>/', VivaConfigViewSet.as_view(), name='total_viva_slot_by_job_id'),
    path('booked-time-slots-via-job-id/<int:job_id>/<date:my_date>/', VivaConfigPerDayViewSet.as_view(),
         name='booked_time_slots_by_date'),
    path('create-job-viva-time-slot/', JobVivaTimeSlotCreateAPIView.as_view(), name='create_job_viva_time_slot'),
    path('candidate/<int:candidate_id>/shortlist/', authentication.UpdateShortlistView.as_view(),
         name='update_shortlist'),
    path('candidate/<int:candidate_id>/call/', authentication.UpdateCallView.as_view(), name='update_call'),
    path('candidate/<int:candidate_id>/schedule/', authentication.UpdateScheduleView.as_view(), name='update_schedule'),
    path('candidate/<int:candidate_id>/feedback/', authentication.UpdateFeedbackView.as_view(), name='update_feedback'),
    path('candidate/<int:candidate_id>/status/', authentication.UpdateStatusView.as_view(), name='update_status'),
]

urlpatterns = [
    path('api/', include(api_urls)),
    path('', include(webview_urls))
]

urlpatterns = format_suffix_patterns(urlpatterns)
