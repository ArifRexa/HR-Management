from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from website.views import ServiceList, ServiceDetails, ProjectList, ProjectDetails, EmployeeList

api_urls = [
    path('services/', ServiceList.as_view(), name='service.list'),
    path('service/<str:slug>/', ServiceDetails.as_view(), name='service.details'),
    path('projects/', ProjectList.as_view(), name='project.list'),
    path('project/<str:slug>/', ProjectDetails.as_view(), name='project.details'),
    path('employees/', EmployeeList.as_view(), name='employee.list'),
]

urlpatterns = [
    path('api/website/', include(api_urls)),
]

urlpatterns = format_suffix_patterns(urlpatterns)
