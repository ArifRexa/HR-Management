from rest_framework.generics import ListAPIView, RetrieveAPIView
from website.serializers_v2.woman_empowerments import EnvironmentSerializer, PhotoSerializer, WomanAchievementSerializer, WomanEmpowermentSerializer, WomanInspirationSerializer
from website.models_v2.woman_empowermens import Environment, Photo, WomanAchievement, WomanEmpowerment, WomanInspiration


class WomanAchievementView(ListAPIView):
    queryset = WomanAchievement.objects.all()
    serializer_class = WomanAchievementSerializer

class WomanInspirationView(ListAPIView):
    queryset = WomanInspiration.objects.all()
    serializer_class = WomanInspirationSerializer

class EnvironmentView(ListAPIView):
    queryset = Environment.objects.all()
    serializer_class = EnvironmentSerializer

class PhotoView(ListAPIView):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

class WomanEmpowermentView(ListAPIView):
    queryset = WomanEmpowerment.objects.all()
    serializer_class = WomanEmpowermentSerializer