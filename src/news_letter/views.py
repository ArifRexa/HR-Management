# src/news_letter/views.py
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from news_letter.models.case_study_subscriber import CaseStudySubscriber
from news_letter.models.subscriber import Subscriber
from news_letter.serializers import CaseStudySubscriptionSerializer, SubscriberSerializer
from project_management.models import Project
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

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
    




# class CaseStudySubscriptionView(APIView):

#     @swagger_auto_schema(
#         operation_summary="Subscribe to case study updates",
#         request_body=CaseStudySubscriptionSerializer,
#         responses={201: "Subscription created", 400: "Validation error", 404: "Project not found"},
#         tags=["Newsletter - Subscribers"]
#     )
#     def post(self, request, *args, **kwargs):
#         serializer = CaseStudySubscriptionSerializer(data=request.data)
#         if serializer.is_valid():
#             project_identifier = serializer.validated_data['project_identifier']
#             email = serializer.validated_data['email']
            
#             try:
#                 # Try to get project by ID first
#                 if project_identifier.isdigit():
#                     project = Project.objects.get(id=project_identifier)
#                 # If not a digit, try to get by slug
#                 else:
#                     project = Project.objects.get(slug=project_identifier)
#             except Project.DoesNotExist:
#                 return Response(
#                     {"error": "Project not found"}, 
#                     status=status.HTTP_404_NOT_FOUND
#                 )
            
#             # Create or update subscription
#             subscription, created = CaseStudySubscriber.objects.update_or_create(
#                 email=email,
#                 defaults={
#                     'project_title': project,
#                     'is_subscribed': True
#                 }
#             )

#             # Send email with PDF if available
#             email_sent = False
#             if project.case_study_pdf:
#                 try:
#                     # Prepare email context
#                     context = {
#                         'project': project,
#                         'subscription': subscription,
#                         # 'site_url': settings.SITE_URL
#                     }
                    
#                     # Render email templates
#                     html_content = render_to_string('emails/case_study_subscription.html', context)
#                     # text_content = render_to_string('emails/case_study_subscription.txt', context)
                    
#                     # Create email message
#                     subject = f"Case Study: {project.title}"
#                     from_email = '"Mediusware-HR" <hr@mediusware.com>'
#                     to_email = [email]
                    
#                     msg = EmailMultiAlternatives(subject, from_email, to_email)
#                     msg.attach_alternative(html_content, "text/html")
                    
#                     # Attach PDF
#                     msg.attach_file(project.case_study_pdf.path)
                    
#                     # Send email
#                     msg.send()
#                     email_sent = True
#                 except Exception as e:
#                     print(f"Error sending email: {str(e)}")
            
#             response_data = {
#                 "email": subscription.email,
#                 "project": project.title,
#                 "subscribed": subscription.is_subscribed,
#                 "created": created,
#                 "email_sent": email_sent
#             }
            
#             return Response(response_data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

class CaseStudySubscriptionView(APIView):

    @swagger_auto_schema(
        operation_summary="Subscribe to case study updates",
        request_body=CaseStudySubscriptionSerializer,
        responses={201: "Subscription created", 400: "Validation error", 404: "Project not found"},
        tags=["Newsletter - Subscribers"]
    )
    def post(self, request, *args, **kwargs):
        serializer = CaseStudySubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            project_identifier = serializer.validated_data['project_identifier']
            email = serializer.validated_data['email']
            
            try:
                # Try to get project by ID first
                if project_identifier.isdigit():
                    project = Project.objects.get(id=project_identifier)
                # If not a digit, try to get by slug
                else:
                    project = Project.objects.get(slug=project_identifier)
            except Project.DoesNotExist:
                return Response(
                    {"error": "Project not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create or update subscription
            subscription = CaseStudySubscriber.objects.create(
                    email=email,
                    project_title=project,
                    is_subscribed=True
                )

            # Send email with PDF if available
            email_sent = False
            if project.case_study_pdf_link:
                try:
                    # Prepare email context
                    context = {
                        'project': project,
                        'subscription': subscription,
                        'site_url': 'https://mediusware.com'  # Replace with your actual domain
                    }
                    
                    # Render HTML template with full path including app name
                    html_content = render_to_string('emails/case_study_subscription.html', context)
                    
                    # Create plain text version from HTML
                    text_content = strip_tags(html_content)
                    
                    # Create email message with correct parameters
                    subject = f"Case Study: {project.title}"
                    from_email = '"Mediusware-HR" <hr@mediusware.com>'
                    to_email = [email]
                    
                    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
                    msg.attach_alternative(html_content, "text/html")
                    
                    # Attach PDF
                    msg.attach_file(project.case_study_pdf_link.path)
                    
                    # Send email
                    msg.send()
                    email_sent = True
                except Exception as e:
                    print(f"Error sending email: {str(e)}")
            
            response_data = {
                "email": subscription.email,
                "project": project.title,
                "subscribed": subscription.is_subscribed,
                "email_sent": email_sent
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


