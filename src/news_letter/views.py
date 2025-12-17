# src/news_letter/views.py
from django.shortcuts import get_object_or_404
from django.urls import reverse
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
from django.utils import timezone





class VerifySubscriberView(APIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="Verify a subscriber via token",
        operation_description="Marks the subscriber as verified using a one-time token.",
        responses={200: "Email verified successfully", 404: "Invalid token"},
        tags=["Newsletter - Subscribers"]
    )
    def get(self, request, token):
        subscriber = get_object_or_404(Subscriber, verification_token=token)
        if subscriber.is_verified:
            return Response({"message": "Already verified."}, status=status.HTTP_200_OK)

        subscriber.is_verified = True
        subscriber.save(update_fields=['is_verified'])
        return Response({"message": "Email verified successfully!"}, status=status.HTTP_200_OK)



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
        email = request.data.get('email', '').strip().lower()
        
        if not email:
            return Response({"email": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Normalize email (optional but recommended)
        try:
            subscriber = Subscriber.objects.get(email=email)
            
            if subscriber.is_verified:
                # Case 1: Already verified
                serializer = SubscriberSerializer(subscriber)
                return Response(
                    {
                        "message": "You're already subscribed and verified! Thank you for your interest.",
                        "subscriber": serializer.data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                # Case 2: Exists but not verified → resend email
                # (Optionally update verification_token to prevent old link abuse)
                from uuid import uuid4
                subscriber.verification_token = uuid4()
                subscriber.save(update_fields=['verification_token'])

        except Subscriber.DoesNotExist:
            # Case 3: New subscriber
            serializer = SubscriberSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            subscriber = serializer.save(is_subscribed=True, is_verified=False)

        # For both Case 2 & 3: Send verification email
        verify_url = request.build_absolute_uri(
            reverse('verify-subscriber', kwargs={'token': str(subscriber.verification_token)})
        )

        html_content = render_to_string(
            "emails/verify_subscription_email.html",
            {
                "verify_url": verify_url,
                "email": subscriber.email,
                "current_year": timezone.now().year,
            }
        )

        subject = "Verify Your Newsletter Subscription"
        from_email = '"Mediusware-HR" <hr@mediusware.com>'
        to_email = [subscriber.email]

        email = EmailMultiAlternatives(
            subject=subject,
            body="Please verify your subscription by clicking the link in the HTML version of this email.",
            from_email=from_email,
            to=to_email,
        )
        email.attach_alternative(html_content, "text/html")

        try:
            email.send()
        except Exception as e:
            print(f"Failed to send verification email to {subscriber.email}: {str(e)}")
            # Optionally return 500, but usually we still return 201/200 to avoid leaking email validity

        # Return consistent response for new and unverified (to avoid email enumeration)
        return Response(
            {
                "message": "Verification email sent! Please check your inbox to confirm your subscription.",
                "email": subscriber.email
            },
            status=status.HTTP_200_OK if hasattr(subscriber, 'id') and not subscriber.is_verified else status.HTTP_201_CREATED
        )



    # def post(self, request):
    #     serializer = SubscriberSerializer(data=request.data)
    #     if serializer.is_valid():
    #         subscriber = serializer.save(is_subscribed=True, is_verified=False)

    #         # Build verification URL
    #         verify_url = request.build_absolute_uri(
    #             reverse('verify-subscriber', kwargs={'token': str(subscriber.verification_token)})
    #         )

    #         # Render HTML email
    #         html_content = render_to_string(
    #             "emails/verify_subscription_email.html",
    #             {
    #                 "verify_url": verify_url,
    #                 "email": subscriber.email,
    #                 "current_year": timezone.now().year,
    #             }
    #         )

    #         # Create and send email
    #         subject = "Verify Your Newsletter Subscription"
    #         from_email = '"Mediusware-HR" <hr@mediusware.com>'
    #         to_email = [subscriber.email]

    #         email = EmailMultiAlternatives(
    #             subject=subject,
    #             body="Please verify your subscription by clicking the link in the HTML version of this email.",
    #             from_email=from_email,
    #             to=to_email,
    #         )
    #         email.attach_alternative(html_content, "text/html")

    #         try:
    #             email.send()
    #         except Exception as e:
    #             # Optional: log the error (e.g., using logging module)
    #             print(f"Failed to send verification email to {subscriber.email}: {str(e)}")

    #         return Response(serializer.data, status=status.HTTP_201_CREATED)

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    





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


