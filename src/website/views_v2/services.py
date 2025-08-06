from rest_framework.generics import ListAPIView, RetrieveAPIView

from website.models_v2.services import ServicePage
from website.serializers_v2.services import ServicePageDetailSerializer, ServicePageSerializer, ServicePageSitemapSerializer


class ServiceListView(ListAPIView):
    queryset = ServicePage.objects.filter(parent__isnull=True)
    serializer_class = ServicePageSerializer

class ServicePageSitemapListView(ListAPIView):
    queryset = ServicePage.objects.filter(parent__isnull=False)
    serializer_class = ServicePageSitemapSerializer
    pagination_class = None


class ServicePageDetailView(RetrieveAPIView):
    queryset = ServicePage.objects.all()
    serializer_class = ServicePageDetailSerializer
    # lookup_url_kwarg = "slug"
    lookup_field = "slug"


from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .services import ServicePage

@staff_member_required
def get_child_services(request):
    parent_ids = request.GET.get('parent_ids', '').split(',')
    parent_ids = [pid for pid in parent_ids if pid.isdigit()]
    child_services = ServicePage.objects.filter(parent__id__in=parent_ids, is_parent=False).values('id', 'title')
    return JsonResponse({'child_services': list(child_services)})