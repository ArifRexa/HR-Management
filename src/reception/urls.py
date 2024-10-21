from django.urls import path
from . import views

urlpatterns = [
    path('scan/', views.generate_random_link, name='generate_random_link'),
    path('form/<str:unique_url>/', views.visitor_form, name='visitor_form'),
    path('success/', views.success_page, name='success_page'),
    path('ajax/pending-reception-count/', views.pending_reception_count, name='pending_reception_count'),
]
