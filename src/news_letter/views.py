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
    