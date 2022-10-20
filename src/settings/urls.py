from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from settings import views

api_url = [
    # path('open-letter/', views.OpenLetterView.as_view())
]

urlpatterns = [
    # path('api/', include(api_url))
]

urlpatterns = format_suffix_patterns(urlpatterns)
