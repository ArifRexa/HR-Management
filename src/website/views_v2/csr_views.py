from rest_framework.generics import ListAPIView, RetrieveAPIView

from website.csr_models import CSR,OurEffort,OurEvent
from website.serializers_v2.csr_serializer import CSRSerializer,OurEffortSerializer,OurEventSerializer


class CSRListAPIView(ListAPIView):
    queryset = CSR.objects.all()
    serializer_class = CSRSerializer

class OurEventListAPIView(ListAPIView):
    queryset = OurEvent.objects.all()
    serializer_class = OurEventSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

class OurEffortListAPIView(ListAPIView):
    queryset = OurEffort.objects.all()
    serializer_class = OurEffortSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context