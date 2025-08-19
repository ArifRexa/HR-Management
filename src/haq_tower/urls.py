from django.urls import path

from src.haq_tower.admin import MotherBillAdmin


urlpatterns = [
    path('generate-pdf/', MotherBillAdmin.as_view(), name='generate_pdf'),
]
