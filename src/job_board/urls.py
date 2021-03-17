from django.contrib import admin
from django.urls import path, include
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('jobs', views.jobs, name='jobs'),
    path('jobs/job-details/<int:id>', views.jobDetails.as_view(), name='job-details'),
    path('jobs/job-apply/<int:id>', views.jobApply.as_view(), name='job-apply'),

]
