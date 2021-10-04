from django.shortcuts import render

# Create your views here.
from rest_framework import generics

from settings.serializers import OpenLetterSerializer


class OpenLetterView(generics.CreateAPIView):
    serializer_class = OpenLetterSerializer
