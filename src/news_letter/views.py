# # src/news_letter/views.py

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from drf_yasg.utils import swagger_auto_schema
# from drf_yasg import openapi

# from news_letter.models.subscriber import Subscriber
# from news_letter.serializers import SubscriberSerializer


# class SubscriberAPIView(APIView):

#     @swagger_auto_schema(
#         operation_summary="List all subscribers or retrieve one by ID",
#         operation_description=(
#             "• GET `/subscribers/` → returns list of all subscribers.\n"
#             "• GET `/subscribers/{id}/` → returns a single subscriber by numeric ID."
#         ),
#         manual_parameters=[
#             openapi.Parameter(
#                 'identifier',
#                 openapi.IN_PATH,
#                 description="Numeric ID of the subscriber (e.g., 5). Omit for full list.",
#                 type=openapi.TYPE_INTEGER,
#                 # required=False,
#             )
#         ],
#         responses={
#             200: openapi.Response(
#                 description="Successful response (list or single object)",
#                 # Note: Swagger can't perfectly show both shapes, so we describe it textually
#             ),
#             404: "Subscriber not found (when ID is provided but invalid)",
#         },
#         tags=["Newsletter - Subscribers"]
#     )
#     def get(self, request, identifier=None):
#         try:
#             if identifier is not None:
#                 if not str(identifier).isdigit():
#                     return Response(
#                         {"error": "Identifier must be a numeric ID."},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )
#                 subscriber = Subscriber.objects.get(id=int(identifier))
#                 serializer = SubscriberSerializer(subscriber)
#                 return Response(serializer.data)
#             else:
#                 subscribers = Subscriber.objects.all()
#                 serializer = SubscriberSerializer(subscribers, many=True)
#                 return Response(serializer.data)

#         except Subscriber.DoesNotExist:
#             return Response(
#                 {"error": "Subscriber not found"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         except Exception as e:
#             return Response(
#                 {"error": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

#     @swagger_auto_schema(
#         operation_summary="Create a new subscriber",
#         operation_description="Subscribe a new email to the newsletter.",
#         request_body=SubscriberSerializer,
#         responses={
#             201: SubscriberSerializer,
#             400: "Validation error (e.g., duplicate email)",
#         },
#         tags=["Newsletter - Subscribers"]
#     )
#     def post(self, request, identifier=None):
#         if identifier is not None:
#             return Response(
#                 {"error": "POST not allowed with identifier."},
#                 status=status.HTTP_405_METHOD_NOT_ALLOWED
#             )
#         serializer = SubscriberSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     @swagger_auto_schema(
#         operation_summary="Update a subscriber (full)",
#         operation_description="Update all fields of an existing subscriber by ID.",
#         request_body=SubscriberSerializer,
#         responses={
#             200: SubscriberSerializer,
#             400: "Validation error",
#             404: "Subscriber not found",
#         },
#         tags=["Newsletter - Subscribers"]
#     )
#     def put(self, request, identifier=None):
#         if identifier is None:
#             return Response(
#                 {"error": "PUT requires an identifier (subscriber ID)."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         try:
#             subscriber = Subscriber.objects.get(id=identifier)
#             serializer = SubscriberSerializer(subscriber, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Subscriber.DoesNotExist:
#             return Response(
#                 {"error": "Subscriber not found"},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#     @swagger_auto_schema(
#         operation_summary="Partially update a subscriber",
#         operation_description="Update only specified fields of a subscriber by ID.",
#         request_body=SubscriberSerializer,
#         responses={
#             200: SubscriberSerializer,
#             400: "Validation error",
#             404: "Subscriber not found",
#         },
#         tags=["Newsletter - Subscribers"]
#     )
#     def patch(self, request, identifier=None):
#         if identifier is None:
#             return Response(
#                 {"error": "PATCH requires an identifier (subscriber ID)."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         try:
#             subscriber = Subscriber.objects.get(id=identifier)
#             serializer = SubscriberSerializer(subscriber, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Subscriber.DoesNotExist:
#             return Response(
#                 {"error": "Subscriber not found"},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#     @swagger_auto_schema(
#         operation_summary="Delete a subscriber",
#         operation_description="Permanently remove a subscriber by ID.",
#         responses={
#             204: "No Content",
#             404: "Subscriber not found",
#         },
#         tags=["Newsletter - Subscribers"]
#     )
#     def delete(self, request, identifier=None):
#         if identifier is None:
#             return Response(
#                 {"error": "DELETE requires an identifier (subscriber ID)."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         try:
#             subscriber = Subscriber.objects.get(id=identifier)
#             subscriber.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except Subscriber.DoesNotExist:
#             return Response(
#                 {"error": "Subscriber not found"},
#                 status=status.HTTP_404_NOT_FOUND
#             )




# src/news_letter/views.py

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from news_letter.models.subscriber import Subscriber
from news_letter.serializers import SubscriberSerializer


class SubscriberListView(APIView):
    @swagger_auto_schema(
        operation_summary="List all subscribers",
        operation_description="Returns a list of all newsletter subscribers.",
        responses={200: SubscriberSerializer(many=True)},
        tags=["Newsletter - Subscribers"]
    )
    def get(self, request):
        subscribers = Subscriber.objects.all()
        serializer = SubscriberSerializer(subscribers, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create a new subscriber",
        request_body=SubscriberSerializer,
        responses={201: SubscriberSerializer, 400: "Validation error (e.g., duplicate email)"},
        tags=["Newsletter - Subscribers"]
    )
    def post(self, request):
        serializer = SubscriberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriberDetailView(APIView):
    @swagger_auto_schema(
        operation_summary="Retrieve a subscriber by ID",
        operation_description="Get a single subscriber using their numeric ID.",
        responses={200: SubscriberSerializer, 404: "Subscriber not found"},
        tags=["Newsletter - Subscribers"]
    )
    def get(self, request, identifier):
        subscriber = get_object_or_404(Subscriber, id=identifier)
        serializer = SubscriberSerializer(subscriber)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Update a subscriber (full)",
        request_body=SubscriberSerializer,
        responses={200: SubscriberSerializer, 400: "Validation error", 404: "Not found"},
        tags=["Newsletter - Subscribers"]
    )
    def put(self, request, identifier):
        subscriber = get_object_or_404(Subscriber, id=identifier)
        serializer = SubscriberSerializer(subscriber, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Partially update a subscriber",
        request_body=SubscriberSerializer,
        responses={200: SubscriberSerializer, 400: "Validation error", 404: "Not found"},
        tags=["Newsletter - Subscribers"]
    )
    def patch(self, request, identifier):
        subscriber = get_object_or_404(Subscriber, id=identifier)
        serializer = SubscriberSerializer(subscriber, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete a subscriber",
        responses={204: "No content", 404: "Subscriber not found"},
        tags=["Newsletter - Subscribers"]
    )
    def delete(self, request, identifier):
        subscriber = get_object_or_404(Subscriber, id=identifier)
        subscriber.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)