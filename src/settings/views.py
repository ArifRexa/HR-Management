from django.shortcuts import render

# Create your views here.
from rest_framework import generics

from settings.serializers import OpenLetterSerializer


class OpenLetterView(generics.CreateAPIView):
    serializer_class = OpenLetterSerializer

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import os
from django.conf import settings
from uuid import uuid4

@csrf_exempt
def upload_image(request):
    if request.method != "POST":
        return JsonResponse({'Error Message': "Wrong request"})
    
    file_obj = request.FILES['file']
    file_name_suffix = file_obj.name.split(".")[-1]
    if file_name_suffix not in ["jpg", "png", "gif", "jpeg"]:
        return JsonResponse({"Error Message": f"Wrong file suffix ({file_name_suffix}), supported are .jpg, .png, .gif, .jpeg"})

    directory = os.path.join(settings.MEDIA_ROOT, 'uploads')
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file_obj.name)

    if os.path.exists(file_path):
        file_obj.name = str(uuid4()) + '.' + file_name_suffix
        file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file_obj.name)

    with open(file_path, 'wb+') as f:
        for chunk in file_obj.chunks():
            f.write(chunk)

        return JsonResponse({
            'message': 'Image uploaded successfully',
            'location': os.path.join(settings.MEDIA_URL, 'uploads', file_obj.name)
        })