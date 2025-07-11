from django.urls import include, path
from rest_framework import routers

from .views import (
    ClientViewSet,
    CountryViewSet,
    CurrencyListView,
    DailyProjectUpdateViewSet,
    ProjectViewSet,
    WeeklyProjectUpdateViewSet,
    ClientReviewViewSet,
    ProjectResourceListView,
    PaymentMethodListView,
    InvoiceTypeListView,
)

router = routers.DefaultRouter()

router.register("daily-project-update", DailyProjectUpdateViewSet)
router.register("project-update", WeeklyProjectUpdateViewSet, basename="project-update")
router.register("resources", ProjectResourceListView, basename="project-resources")
router.register("projects", ProjectViewSet, basename="projects")
router.register("clients", ClientViewSet, basename="clients")
router.register("countries", CountryViewSet, basename="countries")
router.register("client-reviews", ClientReviewViewSet, basename="client-reviews")



urlpatterns = [
    path("", include(router.urls)),
    path("currency", CurrencyListView.as_view(), name="currency"),
    path("payment-methods", PaymentMethodListView.as_view(), name="payment-method-list"),
    path("invoice-types", InvoiceTypeListView.as_view(), name="invoice-type-list"),
]
