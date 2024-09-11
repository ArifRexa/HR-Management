from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import os
from django.conf import settings
from uuid import uuid4
import config.settings
from io import BytesIO
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Create your views here.
from rest_framework import generics

from settings.serializers import OpenLetterSerializer


class OpenLetterView(generics.CreateAPIView):
    serializer_class = OpenLetterSerializer


@csrf_exempt
def upload_image(request):
    if request.method != "POST":
        return JsonResponse({"Error Message": "Wrong request"})

    file_obj = request.FILES["file"]
    file_name_suffix = file_obj.name.split(".")[-1]
    if file_name_suffix not in ["jpg", "png", "gif", "jpeg"]:
        return JsonResponse(
            {
                "Error Message": f"Wrong file suffix ({file_name_suffix}), supported are .jpg, .png, .gif, .jpeg"
            }
        )

    directory = os.path.join(settings.MEDIA_ROOT, "uploads")
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(settings.MEDIA_ROOT, "uploads", file_obj.name)

    if os.path.exists(file_path):
        file_obj.name = str(uuid4()) + "." + file_name_suffix
        file_path = os.path.join(settings.MEDIA_ROOT, "uploads", file_obj.name)

    with open(file_path, "wb+") as f:
        for chunk in file_obj.chunks():
            f.write(chunk)

        return JsonResponse(
            {
                "message": "Image uploaded successfully",
                "location": os.path.join(settings.MEDIA_URL, "uploads", file_obj.name),
            }
        )


@csrf_exempt
def tinymce_image_upload(request):
    if request.method != "POST":
        return JsonResponse({"Error Message": "Wrong request"})

    file_obj = request.FILES["file"]
    file_name_suffix = file_obj.name.split(".")[-1]
    if file_name_suffix not in ["jpg", "png", "gif", "jpeg"]:
        return JsonResponse(
            {
                "Error Message": f"Wrong file suffix ({file_name_suffix}), supported are .jpg, .png, .gif, .jpeg"
            }
        )

    directory = os.path.join(settings.MEDIA_ROOT, "uploads")
    if config.settings.DEFAULT_S3_CLIENT:
        s3_client = config.settings.DEFAULT_S3_CLIENT
        file_byte_obj = BytesIO(file_obj.read())
        file_byte_obj.seek(0)
        # Upload the file-like object to the Space
        try:
            s3_client.upload_fileobj(
                # s3_client.upload_file(
                file_byte_obj,
                config.settings.AWS_STORAGE_BUCKET_NAME,
                # self.absolute_file_path(),
                f"media/uploads/{file_obj.name}",
                ExtraArgs={"ContentType": file_obj.content_type, "ACL": "public-read"},
            )
        except Exception as e:
            print("Upload error: ", e)
        file_url = f"{config.settings.MEDIA_URL}uploads/{file_obj.name}"
        print("at file upload: ", file_url, file_name_suffix)
        # print('at filename: ', bytecode.getvalue())
        return JsonResponse(
            {"message": "Image uploaded successfully", "location": file_url}
        )

    else:
        if not os.path.exists(directory):
            os.makedirs(directory)

        file_path = os.path.join(settings.MEDIA_ROOT, "uploads", file_obj.name)

        if os.path.exists(file_path):
            file_obj.name = str(uuid4()) + "." + file_name_suffix
            file_path = os.path.join(settings.MEDIA_ROOT, "uploads", file_obj.name)
        # file_path = f"{directory}/{file_obj.name}"
        saved_path = default_storage.save(file_path, ContentFile(file_obj.read()))
        print("saved_path: ", file_path)
        return JsonResponse(
            {
                "message": "Image uploaded successfully",
                "location": os.path.join(settings.MEDIA_URL, "uploads", file_obj.name),
            }
        )
